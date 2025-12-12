# ===================== PecanStreet DataBuilder =====================#
class PecanStreet_DataBuilder(object):
    def __init__(
        self,
        data_path,
        mask_app,
        sampling_rate,
        window_size,
        window_stride=None,
        soft_label=False,
    ):
        self.data_path = data_path
        self.mask_app = mask_app
        self.sampling_rate = sampling_rate
        self.window_size = window_size
        self.soft_label = soft_label

        if isinstance(self.mask_app, str):
            self.mask_app = [self.mask_app]

        if window_stride is not None:
            self.window_stride = window_stride
        else:
            self.window_stride = self.window_size

        # Add aggregate to appliance list
        self.mask_app = ["grid"] + self.mask_app

        # Dataset Parameters
        self.cutoff = 10000
        
        # Appliance thresholds (in kW - data is in kilowatts)
        self.appliance_param = {
            "dishwasher1": {"min_threshold": 0.020, "max_threshold": 1.500},
            "air1": {"min_threshold": 0.030, "max_threshold": 3.500},
            "clotheswasher1": {"min_threshold": 0.020, "max_threshold": 0.300},
            "refrigerator1": {"min_threshold": 0.020, "max_threshold": 0.200},
            "microwave1": {"min_threshold": 0.015, "max_threshold": 1.600},
        }

    def get_nilm_dataset(self, house_indicies):
        """
        Process data to build NILM dataset
        Returns: data array (N, M_appliances, 2, L) and start dates
        """
        output_data = np.array([])
        st_date = pd.DataFrame()

        for indice in house_indicies:
            tmp_list_st_date = []
            data = self._get_dataframe(indice)
            stems, st_date_stems = self._get_stems(data)

            if self.window_size == self.window_stride:
                n_wins = len(data) // self.window_stride
            else:
                n_wins = 1 + ((len(data) - self.window_size) // self.window_stride)

            X = np.empty(
                (len(house_indicies) * n_wins, len(self.mask_app), 2, self.window_size)
            )

            cpt = 0
            for i in range(n_wins):
                tmp = stems[
                    :,
                    i * self.window_stride : i * self.window_stride + self.window_size,
                ]

                if not self._check_anynan(tmp):
                    # Skip windows where appliance is completely OFF
                    appliance_status = tmp[2::2, :]  # All appliance status rows (starting from row 2)
                    if appliance_status.sum() == 0:  # All OFF window
                        continue
                    
                    tmp_list_st_date.append(st_date_stems[i * self.window_stride])

                    X[cpt, 0, 0, :] = tmp[0, :]
                    X[cpt, 0, 1, :] = (tmp[0, :] > 0).astype(dtype=int)

                    key = 1
                    for j in range(1, len(self.mask_app)):
                        X[cpt, j, 0, :] = tmp[key, :]
                        X[cpt, j, 1, :] = tmp[key + 1, :]
                        key += 2

                    cpt += 1

            tmp_st_date = pd.DataFrame(
                data=tmp_list_st_date,
                index=[indice for _ in range(cpt)],
                columns=["start_date"],
            )
            output_data = (
                np.concatenate((output_data, X[:cpt, :, :, :]), axis=0)
                if output_data.size
                else X[:cpt, :, :, :]
            )
            st_date = (
                pd.concat([st_date, tmp_st_date], axis=0)
                if st_date.size
                else tmp_st_date
            )

        return output_data, st_date

    def _get_dataframe(self, indice):
        """Load and process house data"""
        file = self.data_path + "1minute_data_austin.csv"
        
        # Load only this house
        df = pd.read_csv(file)
        df['localminute'] = pd.to_datetime(df['localminute'], utc=True)
        house_data = df[df['dataid'] == indice].copy()
        house_data = house_data.set_index('localminute').sort_index()
        
        # Fill missing values
        house_data = house_data.resample('1min').mean().ffill(limit=5)
        
        # Add solar to grid to get true load
        if 'solar' in house_data.columns:
            solar_total = house_data['solar'].fillna(0).abs()
            if 'solar2' in house_data.columns:
                solar_total += house_data['solar2'].fillna(0).abs()
            house_data['grid'] = house_data['grid'] + solar_total
        
        # Apply 5W threshold only to grid (not appliances)
        house_data['grid'] = house_data['grid'].clip(lower=0)
        house_data.loc[house_data['grid'] < 0.005, 'grid'] = 0  # Fix chained assignment
        house_data['grid'] = house_data['grid'].clip(upper=self.cutoff)

        # Create status for each appliance
        for appliance in self.mask_app[1:]:
            if appliance in house_data.columns:
                # Clip appliance to valid range and remove negatives
                house_data[appliance] = house_data[appliance].fillna(0).clip(lower=0, upper=self.cutoff)
                
                # Create status based on thresholds
                initial_status = (
                    (house_data[appliance] >= self.appliance_param[appliance]["min_threshold"])
                    & (house_data[appliance] <= self.appliance_param[appliance]["max_threshold"])
                ).astype(int)
                
                if not self.soft_label:
                    house_data[appliance + "_status"] = initial_status
                else:
                    house_data[appliance + "_status"] = initial_status.astype(float)
            else:
                house_data[appliance] = 0
                house_data[appliance + "_status"] = 0

        return house_data

    def _get_stems(self, dataframe):
        """Extract load curves and status for each appliance"""
        stems = np.empty((1 + (len(self.mask_app) - 1) * 2, dataframe.shape[0]))
        stems[0, :] = dataframe["grid"].values

        key = 1
        for appliance in self.mask_app[1:]:
            stems[key, :] = dataframe[appliance].values
            stems[key + 1, :] = dataframe[appliance + "_status"].values
            key += 2

        return stems, list(dataframe.index)

    def _check_anynan(self, a):
        """Fast check for NaN in numpy array"""
        return np.isnan(np.sum(a))