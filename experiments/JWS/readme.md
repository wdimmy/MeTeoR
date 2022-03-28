**Using MeTeoR to do the streaming reasoning**

```shell
python meteor_mock.py --datapath ./traffic1.txt --rulepath ./programs/efficient_shortbreak.txt
--datasetname traffic_shortbreak_small --target ShortBreak
```
Some intermediate results will be saved in ./results/meteor_traffic_shortbreak_small.pkl, which is a dictionary containing
the following information:

```
window_size: a integer list recording the window_size at each rule application iteration after coalescing
window_size_raw: a integer list recording the window_size at each rule application iteration before coalescing
```
--------------------------------------------------------------------------------
**Using MeTeoR_Str to do the streaming reasoning**

```shell
python sr_mock.py --datapath ./traffic1.txt --rulepath ./programs/efficient_shortbreak.txt
--datasetname traffic_shortbreak_small --target ShortBreak
```
Some intermediate results will be saved in ./results/sr_traffic_shortbreak_small.pkl, which is a dictionary containing the
following information:
```
window_size: a integer list recording the window_size at each time point after coalescing
window_size_raw: a integer list recording the window_size  at each time point before coalescing
run_times: a float list recording the run time at each time point
```

--------------------------------------------------------------------------------

Due to the space limitation of the Github repository, we only provide the dataset S_1, and for the other five datasets
used in our paper: D_1, D_2, D_3, D_4 and S_2, feel free to contact dingmin.wang@cs.ox.ac.uk. 
