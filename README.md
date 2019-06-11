# VPO1 form reader


Utils to extract that from VPO1[^vpo1] forms that contain aggregated data about
skills taught by Russian universities.


[^vpo1]: https://minobrnauki.gov.ru/ru/activity/statan/stat/highed/


TODO:

1. [x] Reading XLS; Finding the dataframe and the metadata in VPO-1
1. [ ] Merging VPO-1 form into array of sections (e.g. 2.1.2 "distribution of students over courses, programs, specialities", etc) which are spread over multiple sheets.
1. [ ] Stripping the "total no." and other aggregates out of dataframe
1. [ ] Lazy read, iteration
1. [ ] Download function
