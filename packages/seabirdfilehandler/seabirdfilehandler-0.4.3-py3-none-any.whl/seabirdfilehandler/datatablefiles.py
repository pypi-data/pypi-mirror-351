from pathlib import Path
from typing import Union, Tuple
from datetime import datetime, time, timedelta
import re
import pandas as pd
import numpy as np
import logging
import warnings
from seabirdfilehandler.parameter import Parameters
from seabirdfilehandler.validation_modules import CnvValidationList
from seabirdfilehandler.seabirdfiles import SeaBirdFile
from seabirdfilehandler.dataframe_meta_accessor import (
    SeriesMetaAccessor,  # noqa: F401
    DataFrameMetaAccessor,  # noqa: F401
)

logger = logging.getLogger(__name__)


class DataTableFile(SeaBirdFile):
    """Collection of methods for the SeaBird files that feature some kind of
    data table that is represented in a pandas dataframe.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, path_to_file):
        super().__init__(path_to_file)
        self.original_df: pd.DataFrame
        self.df: pd.DataFrame

    def define_output_path(
        self,
        file_path: Path | str | None = None,
        file_name: str | None = None,
        file_type: str = ".csv",
    ) -> Path:
        """Creates a Path object holding the desired output path.

        Parameters
        ----------
        file_path : Path :
            directory the file sits in (Default value = self.file_dir)
        file_name : str :
            the original file name (Default value = self.file_name)
        file_type : str :
            the output file type (Default = '.csv')
        Returns
        -------
        a Path object consisting of the full path of the new file

        """
        file_path = self.file_dir if file_path is None else file_path
        file_name = self.file_name if file_name is None else file_name
        if file_type[0] != ".":
            file_type = "." + file_type
        return Path(file_path).joinpath(file_name).with_suffix(file_type)

    def to_csv(
        self,
        selected_columns: list | None = None,
        with_header: bool = True,
        output_file_path: Path | str | None = None,
        output_file_name: str | None = None,
    ):
        """Writes a csv from the current dataframe. Takes a list of columns to
        use, a boolean for writing the header and the output file parameters.

        Parameters
        ----------
        selected_columns : list :
            a list of columns to include in the csv
            (Default value = self.df.columns)
        with_header : boolean :
            indicating whether the header shall appear in the output
             (Default value = True)
        output_file_path : Path :
            file directory (Default value = None)
        output_file_name : str :
            original file name (Default value = None)

        Returns
        -------

        """
        selected_columns = (
            self.df.columns if selected_columns is None else selected_columns
        )
        df = self.df[selected_columns].reset_index(drop=True)
        new_file_path = self.define_output_path(
            output_file_path, output_file_name
        )
        if with_header:
            with open(new_file_path, "w") as file:
                for line in self.header:
                    file.write(line)
            df.to_csv(new_file_path, index=False, mode="a")
        else:
            df.to_csv(new_file_path, index=False, mode="w")
        logger.info(f"Wrote file {self.path_to_file} to {new_file_path}.")

    def selecting_columns(
        self,
        list_of_columns: list | str,
        df: pd.DataFrame | None = None,
    ):
        """Alters the dataframe to only hold the given columns.

        Parameters
        ----------
        list_of_columns: list or str : a collection of columns
        df : pandas.Dataframe :
            Dataframe (Default value = None)

        Returns
        -------

        """
        df = self.df if df is None else df
        # ensure that the input is a list, so that isin() can do its job
        if isinstance(list_of_columns, str):
            list_of_columns = [list_of_columns]
        if isinstance(df, pd.DataFrame):
            self.df = df[list_of_columns].reset_index(drop=True)


class BottleFile(DataTableFile):
    """Class that represents a SeaBird Bottle File. Organizes the files table
    information into a pandas dataframe. This allows the usage of this
    powerful library for statistics, visualization, data manipulation, export,
    etc.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, path_to_file):
        super().__init__(path_to_file)
        self.original_df = self.create_dataframe()
        self.df = self.original_df
        self.setting_dataframe_dtypes()
        self.adding_timestamp_column()

    def create_dataframe(self):
        """Creates a dataframe out of the btl file. Manages the double data
        header correctly.

        Parameters
        ----------

        Returns
        -------

        """
        # TODO: this needs to be broken down into smaller pieces...
        top_names, bottom_names = self.reading_data_header()
        # creating statistics column to store the row type information:
        # 4 rows per bottle, average, standard deviation, max value, min value
        top_names.append("Statistic")
        # TODO: sexier way to construct dataframe than opening the file a
        # second time
        # # df = pd.DataFrame(self.data, index=None, columns=top_names)
        df: pd.DataFrame = pd.read_fwf(
            self.path_to_file,
            index_col=False,
            skiprows=len(self.header) + 2,
            header=None,
            names=top_names,
        )

        # handling the double row header
        rowtypes = df[df.columns[-1]].unique()

        # TODO: can this be made a little pretier?
        def separate_double_header_row(df, column, length):
            """

            Parameters
            ----------
            df :
            column :
            length :

            Returns
            -------

            """
            column_idx = df.columns.get_loc(column)
            old_column = df.iloc[::length, column_idx].reset_index(drop=True)
            new_column = df.iloc[1::length, column_idx].reset_index(drop=True)
            old_column_expanded = pd.Series(
                np.repeat(old_column, length)
            ).reset_index(drop=True)
            new_column_expanded = pd.Series(
                np.repeat(new_column, length)
            ).reset_index(drop=True)
            df[column] = old_column_expanded
            df.insert(
                column_idx + 1, bottom_names[column_idx], new_column_expanded
            )
            return df

        df = separate_double_header_row(df, "Date", len(rowtypes))
        df = separate_double_header_row(df, top_names[0], len(rowtypes))
        # remove brackets around statistics values
        df["Statistic"] = df["Statistic"].str.strip("()")
        df = df.rename(mapper={"Btl_ID": "Bottle_ID"}, axis=1)
        return df

    def adding_timestamp_column(self):
        """Creates a timestamp column that holds both, Date and Time
        information.

        Parameters
        ----------

        Returns
        -------

        """
        # constructing timestamp column
        timestamp = []
        for datepoint, timepoint in zip(self.df.Date, self.df.Time):
            timestamp.append(
                datetime.combine(datepoint, time.fromisoformat(str(timepoint)))
            )
        self.df.insert(2, "Timestamp", timestamp)
        self.df.Timestamp = pd.to_datetime(self.df.Timestamp)

    def setting_dataframe_dtypes(self):
        """Sets the types for the column values in the dataframe."""
        # setting dtypes
        # TODO: extending this to the other columns!
        self.df.Date = pd.to_datetime(self.df.Date)
        self.df.Bottle_ID = self.df.Bottle_ID.astype(int)

    def selecting_rows(
        self, df=None, statistic_of_interest: Union[list, str] = ["avg"]
    ):
        """Creates a dataframe with the given row identifier, using the
        statistics column. A single string or a list of strings can be
        processed.

        Parameters
        ----------
        df : pandas.Dataframe :
            the files Pandas representation (Default value = self.df)
        statistic_of_interest: list or str :
            collection of values of the 'statistics' column in self.df
             (Default value = ['avg'])

        Returns
        -------

        """
        df = self.df if df is None else df
        # ensure that the input is a list, so that isin() can do its job
        if isinstance(statistic_of_interest, str):
            statistic_of_interest = [statistic_of_interest]
        self.df = df.loc[df["Statistic"].isin(statistic_of_interest)]

    def reading_data_header(self):
        """Identifies and separatly collects the rows that specify the data
        tables headers.

        Parameters
        ----------

        Returns
        -------

        """
        n = 11  # fix column width of a seabird btl file
        top_line = self.data[0]
        second_line = self.data[1]
        top_names = [
            top_line[i : i + n].split()[0]
            for i in range(0, len(top_line) - n, n)
        ]
        bottom_names = [
            second_line[i : i + n].split()[0] for i in range(0, 2 * n, n)
        ]
        return top_names, bottom_names

    def add_station_and_event_column(self):
        event_list = [self.metadata["Station"] for _ in self.data]
        self.df.insert(0, "Event", pd.Series(event_list))

    def add_position_columns(self):
        latitude_list = [self.metadata["GPS_Lat"] for _ in self.data]
        self.df.insert(1, "Latitude", pd.Series(latitude_list))
        longitude_list = [self.metadata["GPS_Lon"] for _ in self.data]
        self.df.insert(2, "Longitude", pd.Series(longitude_list))


class CnvFile(DataTableFile):
    """
    A representation of a cnv-file as used by SeaBird.

    This class intends to fully extract and organize the different types of
    data and metadata present inside of such a file. Downstream libraries shall
    be able to use this representation for all applications concerning cnv
    files, like data processing, transformation or visualization.

    To achieve that, the metadata header is organized by the grandparent-class,
    SeaBirdFile, while the data table is extracted by this class. The data
    representation of choice is a pandas Dataframe. Inside this class, there
    are methods to parse cnv data into dataframes, do the reverse of writing a
    dataframe into cnv compliant form and to manipulate the dataframe in
    various ways.

    Parameters
    ----------
    path_to_file: Path | str:
        the path to the file
    full_data_header: bool:
        whether to use the full data column descriptions for the dataframe
    long_header_names: bool:
        whether to use long header names in the dateframe
    absolute_time_calculation: bool:
        whether to use a real timestamp instead of the second count
    event_log_column: bool:
        whether to add a station and device event column from DSHIP
    coordinate_columns: bool:
        whether to add longitude and latitude from the extra metadata header

    """

    def __init__(
        self,
        path_to_file: Path | str,
        create_dataframe: bool = True,
        absolute_time_calculation: bool = False,
        event_log_column: bool = False,
        coordinate_columns: bool = False,
        data_table_info_level: str = "shortname",
    ):
        super().__init__(path_to_file)
        self.validation_modules = self.obtaining_validation_modules()
        self.start_time = self.reading_start_time()
        if create_dataframe:
            warnings.warn(
                "The default of constructing a pandas Dataframe will soon be replaced by using the Parameters class that works on numpy arrays.",
                DeprecationWarning,
                stacklevel=2,  # Ensures the warning points to the caller's line
            )
            self.data_header_meta_info, self.duplicate_columns = (
                self.reading_data_header(self.data_table_description)
            )
            self.original_df = self.create_dataframe(data_table_info_level)
            self.df = self.original_df
            if absolute_time_calculation:
                self.absolute_time_calculation()
            if event_log_column:
                self.add_station_and_event_column()
            if coordinate_columns:
                self.add_position_columns()
        else:
            self.parameters = Parameters(
                self.data, self.data_table_description
            )

    def reading_data_header(
        self, header_info: list = []
    ) -> Tuple[dict[str, dict], list[int]]:
        """Reads the tables header data from the header.

        Parameters
        ----------
        header_info: list:
            the header values from the file

        Returns
        -------
        a list of dictionaries, that organize the table header information

        """
        if header_info == []:
            header_info = self.data_table_description
        table_header = {}
        duplicate_columns = []
        for line in header_info:
            if line.startswith("name"):
                header_meta_info = {}
                # get basic shortname and the full, non-differentiated info
                shortname = longinfo = line_info = line.split("=")[1].strip()
                try:
                    shortname, longinfo = line_info.split(":")
                except IndexError:
                    pass
                finally:
                    shortname = shortname.strip()
                    if shortname in list(table_header.keys()):
                        try:
                            duplicate_columns.append(
                                int(line.split("=")[0].strip().split()[1])
                            )
                        except IndexError as error:
                            logger.error(
                                f"Could not resolve duplicate column: {
                                    shortname
                                }, {error}"
                            )
                    else:
                        header_meta_info["shortname"] = shortname
                        header_meta_info["longinfo"] = longinfo.strip()
                        metainfo = self._extract_data_header_meta_info(
                            longinfo.strip()
                        )
                        header_meta_info = {**header_meta_info, **metainfo}
                        table_header[shortname.strip()] = header_meta_info
        return table_header, duplicate_columns

    def _extract_data_header_meta_info(self, line: str) -> dict:
        """Extracts the individual information bits inside of the header lines

        Parameters
        ----------
        line: str:
            one header line, trimmed by the 'name =' prefix and the shortname

        Returns
        -------
        a dictionary with the information stored

        """
        regex_string = r"(?:(?P<name0>.+),\s(?P<metainfo0>.+)\s\[(?P<unit0>.+)\]|(?P<name2>.+)\s\[(?P<unit2>.+)\]|(?P<name3>.+),\s(?P<metainfo2>.[^\s]+)|(?P<name4>.+))"
        regex_check = re.search(regex_string, line, flags=re.IGNORECASE)
        if regex_check:
            regex_info = dict(regex_check.groupdict())
            regex_info = {
                key[:-1]: value
                for key, value in regex_info.items()
                if value is not None
            }
            if len(regex_info) > 2:
                # check for second sensors and adjust their names
                if regex_info["metainfo"][-1] == "2":
                    regex_info["name"] = regex_info["name"] + " 2"
                    regex_info["metainfo"] = regex_info["metainfo"][:-1]
                    if len(regex_info["metainfo"]) == 0:
                        regex_info.pop("metainfo")
            if regex_info["name"] == "flag":
                regex_info["metainfo"] = regex_info["name"]
                regex_info["unit"] = regex_info["name"]
            return regex_info
        return {}

    def create_dataframe(
        self,
        header_info_detail_level: str = "shortname",
    ) -> pd.DataFrame:
        """Creates a pandas dataframe by splitting each dataline every 11
        characters, as SeaBird defines its tables this way.

        Parameters
        ----------
        uns_full_header_names: bool:
            whether to use all header information as dataframe header
        uns_long_header_names: bool:
            whether to use header longnames as dataframe header

        Returns
        -------
        a pandas.Dataframe that represents the data values inside the cnv file

        """
        n = 11
        row_list = []
        for line in self.data:
            row_list.append(
                [
                    line[i : i + n].split()[0]
                    for i in range(0, len(line) - n, n)
                ]
            )
        df = pd.DataFrame(row_list, dtype=float)
        header_names = [
            metainfo[header_info_detail_level]
            for metainfo in list(self.data_header_meta_info.values())
        ]
        # remove duplicate columns
        df.drop(labels=self.duplicate_columns, axis=1, inplace=True)
        self.duplicate_columns = []
        try:
            df.columns = header_names
        except ValueError as error:
            logger.error(
                f"Could not set dataframe header for {self.file_name}: {error}"
            )
            logger.error(header_names)
        else:
            df.meta.metadata = self.data_header_meta_info
            # df.meta.propagate_metadata_to_series()
        return df

    def rename_dataframe_header(
        self,
        df: pd.DataFrame | None = None,
        header_detail_level: str = "shortname",
    ) -> list:
        df = self.df if df is None else df
        df.meta.rename(header_detail_level)
        return [column for column in df.columns]

    def reading_start_time(
        self,
        time_source: str = "System UTC",
    ) -> datetime | None:
        """
        Extracts the Cast start time from the metadata header.
        """
        for line in self.sbe9_data:
            if line.startswith(time_source):
                start_time = line.split("=")[1]
                start_time = datetime.strptime(
                    start_time, " %b %d %Y %H:%M:%S "
                )
                return start_time
        return None

    def absolute_time_calculation(self) -> bool:
        """
        Replaces the basic cnv time representation of counting relative to the
        casts start point, by real UTC timestamps.
        This operation will act directly on the dataframe.

        """
        time_parameter = None
        for parameter in self.df.columns:
            if parameter.lower().startswith("time"):
                time_parameter = parameter
        if time_parameter and self.start_time:
            self.df.meta.add_column(
                name="datetime",
                data=[
                    timedelta(days=float(time)) + self.start_time
                    if time_parameter == "timeJ"
                    else timedelta(seconds=float(time)) + self.start_time
                    for time in self.df[time_parameter]
                ],
            )
            return True
        return False

    def add_start_time(self) -> bool:
        """
        Adds the Cast start time to the dataframe.
        Necessary for joins on the time.
        """
        if self.start_time:
            self.df.meta.add_column(
                name="start_time",
                data=pd.Series([self.start_time for _ in self.data]),
            )
            return True
        return False

    def obtaining_validation_modules(self) -> CnvValidationList:
        """
        Collects the individual validation modules and their respective
        information, usually present in key-value pairs.
        """
        validation_modules = self.processing_info
        return CnvValidationList(validation_modules)

    def df2cnv(
        self,
        header_names: list | None = None,
        header_detail_level: str | None = None,
    ) -> list:
        """
        Parses a pandas dataframe into a list that represents the lines inside
        of a cnv data table.

        Parameters
        ----------
        header_names: list:
            a list of dataframe columns that will be parsed

        Returns
        -------
        a list of lines in the cnv data table format

        """
        if not header_detail_level:
            header_detail_level = self.df.meta.header_detail
        if not header_names:
            header_names = [
                header[header_detail_level]
                for header in list(self.data_header_meta_info.values())
            ]
        df = self.df.drop(
            labels=[
                column
                for column in list(self.df.meta.metadata.keys())
                if column not in header_names
            ],
            axis=1,
            errors="ignore",
        )
        cnv_out = []
        for _, row in df.iterrows():
            cnv_like_row = "".join(
                (lambda column: f"{str(column):>11}")(value) for value in row
            )
            cnv_out.append(cnv_like_row + "\n")
        return cnv_out

    def array2cnv(self) -> list:
        result = []
        for row in self.parameters.full_data_array:
            formatted_row = "".join(f"{elem:11}" for elem in row)
            result.append(formatted_row + "\n")
        return result

    def to_cnv(
        self,
        file_name: Path | str | None = None,
        use_dataframe: bool = True,
        header_list: list | None = None,
    ):
        """
        Writes the values inside of this instance as a new cnv file to disc.

        Parameters
        ----------
        file_name: Path:
            the new file name to use for writing
        use_current_df: bool:
            whether to use the current dataframe as data table
        use_current_validation_header: bool:
            whether to use the current processing module list
        header_list: list:
            the data columns to use for the export

        """
        file_name = self.path_to_file if file_name is None else file_name
        # content construction
        if use_dataframe:
            data = self.df2cnv(header_list)
        else:
            data = self.array2cnv()
        self._update_header()
        self.file_data = [*self.header, *data]
        # writing content out
        try:
            with open(file_name, "w", encoding="latin-1") as file:
                for line in self.file_data:
                    file.write(line)

        except IOError as error:
            logger.error(f"Could not write cnv file: {error}")

    def _update_header(self):
        """Re-creates the cnv header."""
        self.data_table_description = self._form_data_table_info()
        self.header = [
            *[f"* {data}" for data in self.sbe9_data[:-1]],
            *[f"** {data}" for data in self.metadata_list],
            f"* {self.sbe9_data[-1]}",
            *[f"# {data}" for data in self.data_table_description],
            *[f"# {data}" for data in self.sensor_data],
            *[f"# {data}" for data in self.processing_info],
            "*END*\n",
        ]

    def _form_data_table_info(self) -> list:
        """Recreates the data table descriptions, like column names and spans
        from the structured dictionaries these values were stored in."""
        new_table_info = []
        for key, value in self.data_table_stats.items():
            new_table_info.append(f"{key} = {value}\n")
        for index, (name, _) in enumerate(self.data_table_names_and_spans):
            new_table_info.append(f"name {index} = {name}\n")
        for index, (_, span) in enumerate(self.data_table_names_and_spans):
            new_table_info.append(f"span {index} = {span}\n")
        for key, value in self.data_table_misc.items():
            new_table_info.append(f"{key} = {value}\n")
        return new_table_info

    def add_processing_metadata(self, addition: str | list):
        """
        Adds new processing lines to the list of processing module information

        Parameters
        ----------
        addition: str:
            the new information line

        """
        # TODO: use CnvprocessingList here
        if isinstance(addition, str):
            addition = [addition]
        for line in addition:
            self.file_data.append(line)
            # add the new info line *before* the 'file_type = ascii' line
            self.processing_info.insert(-1, line)

    def add_station_and_event_column(self) -> bool:
        """
        Adds a column with the DSHIP station and device event numbers to the
        dataframe. These must be present inside the extra metadata header.

        """
        try:
            event_list = [self.metadata["Station"] for _ in self.data]
        except KeyError:
            return False
        else:
            self.df.meta.add_column(
                name="Event", data=pd.Series(event_list), location=0
            )
            return True

    def add_position_columns(self) -> bool:
        """
        Adds a column with the longitude and latitude to the dataframe.
        These must be present inside the extra metadata header.

        """
        if ("latitude" or "longitude") in [
            column["shortname"]
            for column in list(self.df.meta.metadata.values())
        ]:
            return True
        try:
            latitude_list = [self.metadata["GPS_Lat"] for _ in self.data]
            longitude_list = [self.metadata["GPS_Lon"] for _ in self.data]
        except KeyError:
            return False
        else:
            self.df.meta.add_column(
                name="Latitude", data=pd.Series(latitude_list), location=1
            )
            self.df.meta.add_column(
                name="Longitude", data=pd.Series(longitude_list), location=2
            )
            return True

    def add_cast_number(self, number: int | None = None) -> bool:
        """
        Adds a column with the cast number to the dataframe.

        Parameters
        ----------
        number: int:
            the cast number of this files cast

        """
        if ("Cast" in self.metadata.keys()) and (not number):
            number = int(self.metadata["Cast"])
        try:
            self.df.meta.add_column(
                name="Cast",
                data=pd.Series([number for _ in self.data]),
                location=0,
            )
        except ValueError:
            # Cast is already part of the dataframe, so nothing left to do
            return False
        else:
            return True


class BottleLogFile(DataTableFile):
    """Bottle Log file representation, that extracts the three different data
    types from the file: reset time and the table with bottle IDs and
    corresponding data ranges.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(self, path_to_file, create_dataframe=False):
        super().__init__(path_to_file)
        self.reset_time = self.obtaining_reset_time()
        self.origin_cnv = self.raw_file_data[0].strip()
        self.data = self.data_whitespace_removal()

        if create_dataframe:
            self.original_df = self.create_dataframe()
            self.df = self.original_df
        else:
            self.data_list = self.create_list()

    def data_whitespace_removal(self) -> list:
        """Strips the input from whitespace characters, in this case especially
        newline characters.

        Parameters
        ----------

        Returns
        -------
        the original data stripped off the whitespaces

        """
        temp_data = []
        for line in self.raw_file_data[2:]:
            temp_data.append(line.strip())
        return temp_data

    def obtaining_reset_time(self) -> datetime:
        """Reading reset time with small input check.

        Parameters
        ----------

        Returns
        -------
        a datetime.datetime object of the device reset time

        """

        regex_check = re.search(
            r"RESET\s(\w{3}\s\d+\s\d{4}\s\d\d:\d\d:\d\d)",
            self.raw_file_data[1],
        )
        if regex_check:
            return datetime.strptime(regex_check.group(1), "%b %d %Y %H:%M:%S")
        else:
            error_message = """BottleLogFile is not formatted as expected:
                Reset time could not be extracted."""
            logger.error(error_message)
            raise IOError(error_message)

    def create_list(self) -> list:
        """Creates a list of usable data from the list specified in self.data.
        the list consists of: an array of ID's representing the bottles, the date and time of the data sample
        and the lines of the cnv corresponding to the bottles

        Parameters
        ----------

        Returns
        -------
        a list representing the bl files table information
        """
        content_array = []
        for i in range(len(self.data)):
            bottles = [int(x) for x in self.data[i].split(",")[:2]]
            date = self.convert_date(self.data[i].split(",")[2])
            lines = tuple([int(x) for x in self.data[i].split(",")[3:]])

            content_array.append([bottles, date, lines])

        return content_array

    def convert_date(self, date: str):
        """Converts the Dates of the .bl files to an ISO 8601 standard

        Parameters
        ----------

        Returns
        -------
        a string with the date in the form of "yymmddThhmmss"
        """
        date = date.strip()
        month_list = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        month_ind = month_list.index(date.split(" ")[0]) + 1
        if month_ind < 10:
            month = "0" + str(month_ind)
        else:
            month = str(month_ind)
        day = date.split(" ")[1]
        year = (date.split(" ")[2])[2:]
        time = date.split(" ")[3].replace(":", "")
        return year + month + day + "T" + time

    def create_dataframe(self) -> pd.DataFrame:
        """Creates a dataframe from the list specified in self.data.

        Parameters
        ----------

        Returns
        -------
        a pandas.Dataframe representing the bl files table information
        """
        data_lists = []
        for line in self.data:
            inner_list = line.split(",")
            # dropping first column as its the index
            data_lists.append(inner_list[1:])
        df = pd.DataFrame(data_lists)
        df.columns = ["Bottle ID", "Datetime", "start_range", "end_range"]
        return df


class FieldCalibrationFile(DataTableFile):
    def __init__(self, path_to_file):
        super().__init__(path_to_file)
        self.original_df = self.create_dataframe()
        self.df = self.original_df

    def create_dataframe(self) -> pd.DataFrame:
        try:
            return pd.read_csv(self.path_to_file, skiprows=len(self.header))
        except IOError as error:
            logger.error(f"Could not read field calibration file: {error}.")
            return pd.DataFrame()
