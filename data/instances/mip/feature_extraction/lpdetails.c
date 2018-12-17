#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <math.h>
#include <float.h>
#include "containers.h"
#include "macros.h"
#include "lp.h"
#include "lpdetails.h"

static void lpd_compute_svs( int nv, const double *v, SummValues *svs );

static char is_integer( const double v );

void lpd_compute( LinearProgram *mip, LPDetails *lpd )
{
    lpd->cols = lp_cols( mip );
    lpd->rows = lp_rows( mip );
    lpd->equalities = 0;
    lpd->nz = lp_nz( mip );

    lpd->bin = lpd->integer = lpd->continuous = 0;

    for ( int j=0 ; (j<lp_cols(mip) ); ++j )
    {
        if (lp_is_binary(mip, j))
        {
            lpd->bin++;
        }
        else
        {
            if (lp_is_integer(mip, j))
            {
                lpd->integer++;
            }
            else
            {
                lpd->continuous++;
            }
        }
    } // cols

    const double *obj = lp_obj_coef( mip );
    lpd_compute_svs( lp_cols(mip), obj, &(lpd->objSV) );

    double *rhs;
    ALLOCATE_VECTOR( rhs, double, lp_rows(mip)  );
    for ( int i=0 ; (i<lp_rows(mip)) ; ++i )
        rhs[i] = lp_rhs(mip, i);
    lpd_compute_svs( lp_rows(mip), rhs, &(lpd->rhsSV) );
    free( rhs );

    double *A;
    ALLOCATE_VECTOR( A, double, lp_nz(mip) );
    int *idx; double *coef;
    ALLOCATE_VECTOR( idx, int, lp_nz(mip) );
    ALLOCATE_VECTOR( coef, double, lp_nz(mip) );

    int ia=0;
    for ( int i=0 ; (i<lp_rows(mip)) ; ++i )
    {
        int nz = lp_row( mip, i, idx, coef );
        for ( int j=0 ; (j<nz) ; ++j )
            A[ia++] = coef[j];
        if (lp_sense(mip, i)=='E')
            lpd->equalities++;
    }

    assert( ia == lp_nz(mip) );

    lpd_compute_svs( ia, A, &(lpd->ASV) );

    memset( &(lpd->rowsType[0]), 0, sizeof(int)*CONS_NUMBER );
    lp_rows_by_type( mip, &(lpd->rowsType[0]) );

    free( idx );
    free( coef );
    free( A );
}

static int cmp_double( const void *v1, const void *v2 );

void lpd_compute_svs( int nv, const double *v, SummValues *svs )
{
    svs->minv = DBL_MAX;
    svs->maxv = -DBL_MAX;
    svs->allInt = True;

    long double avv = 0.0;

    double *sv;
    ALLOCATE_VECTOR( sv, double, nv );
    
    double minAbsV = DBL_MAX, maxAbsV = -DBL_MAX;
    
    for ( int i=0 ; (i<nv) ; ++i )
    {
        svs->minv = MIN(svs->minv, v[i]);
        svs->maxv = MAX(svs->maxv, v[i]);
        avv += v[i];
        if (is_integer(v[i])==False)
            svs->allInt = False;

        sv[i] = v[i];

        if (fabs(v[i])>=1e-10)
        {
            minAbsV = MIN( minAbsV, fabs(v[i]) );
            maxAbsV = MAX( maxAbsV, fabs(v[i]) );
        }
    }

    svs->ratioLS = maxAbsV / minAbsV;
    
    avv /= ((long double) nv);
    svs->avv = (double)avv;
    
    qsort( sv, nv, sizeof(double), cmp_double );

    svs->median = sv[ nv/2 ];
    
    free( sv );
}


static char is_integer( const double v )
{
    return fabs( v - floor(v+0.5) ) < 1e-10;
}

static int cmp_double( const void *v1, const void *v2 )
{
    const double d1 = *((const double *)v1);
    const double d2 = *((const double *)v2);

    if (fabs(d1-d2)<=1e-20)
        return 0;

    if (d1<d2)
        return -1;
    
    return 1;
}

void svs_write_csv( const SummValues *svs, FILE *f )
{
    fprintf( f, "%g;%g;%g;%g;%d;%g", svs->minv, svs->maxv, svs->avv, svs->median, svs->allInt, svs->ratioLS );
}

void lpd_write_csv_header( FILE *f )
{
    fprintf( f, "name;cols;rows;equalities;nz;bin;int;cont;rpart;rpack;rcov;rcard;rknp;riknp;rflowbin;rflowint;rflowmx;rvbound;rother;" );
    svs_write_csv_header( f, "obj" );
    fprintf( f, ";" );
    svs_write_csv_header( f, "rhs" );
    fprintf( f, ";" );
    svs_write_csv_header( f, "a" );
    fprintf( f, "\n" );
}

void lpd_write_csv( const LPDetails *lpd, FILE *f, const char *name )
{
    fprintf( f, \
     "%s;%d;%d;%d;%d;%d;%d;%d", name, \
     lpd->cols, lpd->rows, lpd->equalities, lpd->nz, lpd->bin, lpd->integer, lpd->continuous \
            );
    for ( int i=0 ; (i<CONS_NUMBER) ; ++i )
        fprintf( f, ";%d", lpd->rowsType[i] );

    fprintf( f, ";" );
    svs_write_csv( &lpd->objSV, f );
    fprintf( f, ";" );
    svs_write_csv( &lpd->rhsSV, f );
    fprintf( f, ";" );
    svs_write_csv( &lpd->ASV, f );
    fprintf( f, "\n" );
}

void svs_write_csv_header( FILE *f, const char *prefix )
{
    fprintf( f, "%sMin;%sMax;%sAv;%sMed;%sAllInt;%sRatioLSA", \
            prefix, prefix, prefix, prefix, prefix, prefix );
}

