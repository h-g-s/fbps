# data/instances/mip/feature\_extraction

This folder contains code to extract features from a Mixed-Integer Program
stored in a .lp or .mps file (possibly compressed with gzip). It outputs
problem features in a new line in the "features.csv" file.

To build call:

``` 
make
```

Example usage:

```
./lpd air04.mps.gz
```

Will compute and store in features.csv all features from instance air04.

