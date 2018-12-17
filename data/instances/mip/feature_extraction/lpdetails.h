#ifndef LPDETAILS
#define LPDETAILS

#include "lp.h"
#include <stdio.h>

// summary of a list of values
typedef struct
{
    double minv;
    double maxv;
    double avv;
    double median;
    char allInt;
    double ratioLS;
} SummValues;

typedef struct 
{
    int cols;
    int rows;
    int equalities;
    int nz;
    int bin;
    int integer;
    int continuous;
    int rowsType[CONS_NUMBER];
    SummValues objSV; // objective 
    SummValues rhsSV; // right hand sides
    SummValues ASV;   // constraint matrix
} LPDetails;

void lpd_compute( LinearProgram *mip, LPDetails *lpd );

void lpd_write_csv_header( FILE *f );

void lpd_write_csv( const LPDetails *lpd, FILE *f, const char *name );

void svs_write_csv( const SummValues *svs, FILE *f );

void svs_write_csv_header( FILE *f, const char *prefix );

#endif

