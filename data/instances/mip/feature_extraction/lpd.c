#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lp.h"
#include "macros.h"
#include "lpdetails.h"
#include "strutils.h"

int main( int argc, char **argv )
{
    if (argc<2)
    {
        printf("enter instance name\n");
        return EXIT_FAILURE;
    }

    LinearProgram *mip = lp_create();
    lp_read(mip, argv[1]);

    char pName[256];
    getFileName( pName, argv[1] );

    {
        char *s = strstr( pName, ".mps.gz" );
        if (s)
            *s = '\0';
    }

    LPDetails lpd;

    char firstLine = True;
    {
        FILE *f = fopen("features.csv", "r");
        if (f)
        {
            firstLine = False;
            fclose(f);
        }
    }

    lpd_compute( mip, &lpd );

    FILE *f = fopen("features.csv", "a");
    if (firstLine)
        lpd_write_csv_header( f );
    lpd_write_csv( &lpd, f, pName );

    fclose(f);

    lp_free( &mip );

    return EXIT_SUCCESS;
}

