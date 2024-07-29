Based on code provided by M. Barnes (ANL)

Code that fits curve around Rmax to find V at Rmax accurately. 
Currently runs through log folder to process all csv's and collect/plot data in newly created folder inside dated folder.
Polynomial based, parameters for fitting:

windows = [25]                  #[1, 3, 5, 10, 25]
polys = [5]                     #[2, 3, 5, 10]
xs = [10000]                    #[10, 100, 1000, 10000] 