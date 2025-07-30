#ifndef NVPL_BLAS_CBLAS_H
#define NVPL_BLAS_CBLAS_H

#include <stddef.h>

#include "nvpl_blas_types.h"

/*
 * Enumerated and derived types
 */
#define CBLAS_INDEX size_t  /* this may vary between platforms */

enum CBLAS_ORDER {CblasRowMajor=101, CblasColMajor=102};
enum CBLAS_TRANSPOSE {CblasNoTrans=111, CblasTrans=112, CblasConjTrans=113};
enum CBLAS_UPLO {CblasUpper=121, CblasLower=122};
enum CBLAS_DIAG {CblasNonUnit=131, CblasUnit=132};
enum CBLAS_SIDE {CblasLeft=141, CblasRight=142};

#ifdef __cplusplus
extern "C" {
#endif

/*
 * ===========================================================================
 * Prototypes for level 1 BLAS functions (complex are recast as routines)
 * ===========================================================================
 */
float  cblas_sdsdot(const nvpl_int_t N, const float alpha, const float *X,
                    const nvpl_int_t incX, const float *Y, const nvpl_int_t incY) NVPL_BLAS_API;
double cblas_dsdot(const nvpl_int_t N, const float *X, const nvpl_int_t incX, const float *Y,
                   const nvpl_int_t incY) NVPL_BLAS_API;
float  cblas_sdot(const nvpl_int_t N, const float  *X, const nvpl_int_t incX,
                  const float  *Y, const nvpl_int_t incY) NVPL_BLAS_API;
double cblas_ddot(const nvpl_int_t N, const double *X, const nvpl_int_t incX,
                  const double *Y, const nvpl_int_t incY) NVPL_BLAS_API;

/*
 * Functions having prefixes Z and C only
 */
void   cblas_cdotu_sub(const nvpl_int_t N, const void *X, const nvpl_int_t incX,
                       const void *Y, const nvpl_int_t incY, void *dotu) NVPL_BLAS_API;
void   cblas_cdotc_sub(const nvpl_int_t N, const void *X, const nvpl_int_t incX,
                       const void *Y, const nvpl_int_t incY, void *dotc) NVPL_BLAS_API;

void   cblas_zdotu_sub(const nvpl_int_t N, const void *X, const nvpl_int_t incX,
                       const void *Y, const nvpl_int_t incY, void *dotu) NVPL_BLAS_API;
void   cblas_zdotc_sub(const nvpl_int_t N, const void *X, const nvpl_int_t incX,
                       const void *Y, const nvpl_int_t incY, void *dotc) NVPL_BLAS_API;


/*
 * Functions having prefixes S D SC DZ
 */
float  cblas_snrm2(const nvpl_int_t N, const float *X, const nvpl_int_t incX) NVPL_BLAS_API;
float  cblas_sasum(const nvpl_int_t N, const float *X, const nvpl_int_t incX) NVPL_BLAS_API;

double cblas_dnrm2(const nvpl_int_t N, const double *X, const nvpl_int_t incX) NVPL_BLAS_API;
double cblas_dasum(const nvpl_int_t N, const double *X, const nvpl_int_t incX) NVPL_BLAS_API;

float  cblas_scnrm2(const nvpl_int_t N, const void *X, const nvpl_int_t incX) NVPL_BLAS_API;
float  cblas_scasum(const nvpl_int_t N, const void *X, const nvpl_int_t incX) NVPL_BLAS_API;

double cblas_dznrm2(const nvpl_int_t N, const void *X, const nvpl_int_t incX) NVPL_BLAS_API;
double cblas_dzasum(const nvpl_int_t N, const void *X, const nvpl_int_t incX) NVPL_BLAS_API;


/*
 * Functions having standard 4 prefixes (S D C Z)
 */
CBLAS_INDEX cblas_isamax(const nvpl_int_t N, const float  *X, const nvpl_int_t incX) NVPL_BLAS_API;
CBLAS_INDEX cblas_idamax(const nvpl_int_t N, const double *X, const nvpl_int_t incX) NVPL_BLAS_API;
CBLAS_INDEX cblas_icamax(const nvpl_int_t N, const void   *X, const nvpl_int_t incX) NVPL_BLAS_API;
CBLAS_INDEX cblas_izamax(const nvpl_int_t N, const void   *X, const nvpl_int_t incX) NVPL_BLAS_API;

/*
 * ===========================================================================
 * Prototypes for level 1 BLAS routines
 * ===========================================================================
 */

/* 
 * Routines with standard 4 prefixes (s, d, c, z)
 */
void cblas_sswap(const nvpl_int_t N, float *X, const nvpl_int_t incX, 
                 float *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_scopy(const nvpl_int_t N, const float *X, const nvpl_int_t incX, 
                 float *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_saxpy(const nvpl_int_t N, const float alpha, const float *X,
                 const nvpl_int_t incX, float *Y, const nvpl_int_t incY) NVPL_BLAS_API;

void cblas_dswap(const nvpl_int_t N, double *X, const nvpl_int_t incX, 
                 double *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_dcopy(const nvpl_int_t N, const double *X, const nvpl_int_t incX, 
                 double *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_daxpy(const nvpl_int_t N, const double alpha, const double *X,
                 const nvpl_int_t incX, double *Y, const nvpl_int_t incY) NVPL_BLAS_API;

void cblas_cswap(const nvpl_int_t N, void *X, const nvpl_int_t incX, 
                 void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_ccopy(const nvpl_int_t N, const void *X, const nvpl_int_t incX, 
                 void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_caxpy(const nvpl_int_t N, const void *alpha, const void *X,
                 const nvpl_int_t incX, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;

void cblas_zswap(const nvpl_int_t N, void *X, const nvpl_int_t incX, 
                 void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_zcopy(const nvpl_int_t N, const void *X, const nvpl_int_t incX, 
                 void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_zaxpy(const nvpl_int_t N, const void *alpha, const void *X,
                 const nvpl_int_t incX, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;


/* 
 * Routines with S and D prefix only
 */
void cblas_srotg(float *a, float *b, float *c, float *s) NVPL_BLAS_API;
void cblas_srotmg(float *d1, float *d2, float *b1, const float b2, float *P) NVPL_BLAS_API;
void cblas_srot(const nvpl_int_t N, float *X, const nvpl_int_t incX,
                float *Y, const nvpl_int_t incY, const float c, const float s) NVPL_BLAS_API;
void cblas_srotm(const nvpl_int_t N, float *X, const nvpl_int_t incX,
                float *Y, const nvpl_int_t incY, const float *P) NVPL_BLAS_API;

void cblas_drotg(double *a, double *b, double *c, double *s) NVPL_BLAS_API;
void cblas_drotmg(double *d1, double *d2, double *b1, const double b2, double *P) NVPL_BLAS_API;
void cblas_drot(const nvpl_int_t N, double *X, const nvpl_int_t incX,
                double *Y, const nvpl_int_t incY, const double c, const double  s) NVPL_BLAS_API;
void cblas_drotm(const nvpl_int_t N, double *X, const nvpl_int_t incX,
                double *Y, const nvpl_int_t incY, const double *P) NVPL_BLAS_API;


/* 
 * Routines with S D C Z CS and ZD prefixes
 */
void cblas_sscal(const nvpl_int_t N, const float alpha, float *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_dscal(const nvpl_int_t N, const double alpha, double *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_cscal(const nvpl_int_t N, const void *alpha, void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_zscal(const nvpl_int_t N, const void *alpha, void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_csscal(const nvpl_int_t N, const float alpha, void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_zdscal(const nvpl_int_t N, const double alpha, void *X, const nvpl_int_t incX) NVPL_BLAS_API;

/*
 * ===========================================================================
 * Prototypes for level 2 BLAS
 * ===========================================================================
 */

/* 
 * Routines with standard 4 prefixes (S, D, C, Z)
 */
void cblas_sgemv(const enum CBLAS_ORDER order,
                 const enum CBLAS_TRANSPOSE TransA, const nvpl_int_t M, const nvpl_int_t N,
                 const float alpha, const float *A, const nvpl_int_t lda,
                 const float *X, const nvpl_int_t incX, const float beta,
                 float *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_sgbmv(const enum CBLAS_ORDER order,
                 const enum CBLAS_TRANSPOSE TransA, const nvpl_int_t M, const nvpl_int_t N,
                 const nvpl_int_t KL, const nvpl_int_t KU, const float alpha,
                 const float *A, const nvpl_int_t lda, const float *X,
                 const nvpl_int_t incX, const float beta, float *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_strmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const float *A, const nvpl_int_t lda, 
                 float *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_stbmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const nvpl_int_t K, const float *A, const nvpl_int_t lda, 
                 float *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_stpmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const float *Ap, float *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_strsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const float *A, const nvpl_int_t lda, float *X,
                 const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_stbsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const nvpl_int_t K, const float *A, const nvpl_int_t lda,
                 float *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_stpsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const float *Ap, float *X, const nvpl_int_t incX) NVPL_BLAS_API;

void cblas_dgemv(const enum CBLAS_ORDER order,
                 const enum CBLAS_TRANSPOSE TransA, const nvpl_int_t M, const nvpl_int_t N,
                 const double alpha, const double *A, const nvpl_int_t lda,
                 const double *X, const nvpl_int_t incX, const double beta,
                 double *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_dgbmv(const enum CBLAS_ORDER order,
                 const enum CBLAS_TRANSPOSE TransA, const nvpl_int_t M, const nvpl_int_t N,
                 const nvpl_int_t KL, const nvpl_int_t KU, const double alpha,
                 const double *A, const nvpl_int_t lda, const double *X,
                 const nvpl_int_t incX, const double beta, double *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_dtrmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const double *A, const nvpl_int_t lda, 
                 double *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_dtbmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const nvpl_int_t K, const double *A, const nvpl_int_t lda, 
                 double *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_dtpmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const double *Ap, double *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_dtrsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const double *A, const nvpl_int_t lda, double *X,
                 const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_dtbsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const nvpl_int_t K, const double *A, const nvpl_int_t lda,
                 double *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_dtpsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const double *Ap, double *X, const nvpl_int_t incX) NVPL_BLAS_API;

void cblas_cgemv(const enum CBLAS_ORDER order,
                 const enum CBLAS_TRANSPOSE TransA, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 const void *X, const nvpl_int_t incX, const void *beta,
                 void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_cgbmv(const enum CBLAS_ORDER order,
                 const enum CBLAS_TRANSPOSE TransA, const nvpl_int_t M, const nvpl_int_t N,
                 const nvpl_int_t KL, const nvpl_int_t KU, const void *alpha,
                 const void *A, const nvpl_int_t lda, const void *X,
                 const nvpl_int_t incX, const void *beta, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_ctrmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const void *A, const nvpl_int_t lda, 
                 void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ctbmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const nvpl_int_t K, const void *A, const nvpl_int_t lda, 
                 void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ctpmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const void *Ap, void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ctrsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const void *A, const nvpl_int_t lda, void *X,
                 const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ctbsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const nvpl_int_t K, const void *A, const nvpl_int_t lda,
                 void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ctpsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const void *Ap, void *X, const nvpl_int_t incX) NVPL_BLAS_API;

void cblas_zgemv(const enum CBLAS_ORDER order,
                 const enum CBLAS_TRANSPOSE TransA, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 const void *X, const nvpl_int_t incX, const void *beta,
                 void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_zgbmv(const enum CBLAS_ORDER order,
                 const enum CBLAS_TRANSPOSE TransA, const nvpl_int_t M, const nvpl_int_t N,
                 const nvpl_int_t KL, const nvpl_int_t KU, const void *alpha,
                 const void *A, const nvpl_int_t lda, const void *X,
                 const nvpl_int_t incX, const void *beta, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_ztrmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const void *A, const nvpl_int_t lda, 
                 void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ztbmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const nvpl_int_t K, const void *A, const nvpl_int_t lda, 
                 void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ztpmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const void *Ap, void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ztrsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const void *A, const nvpl_int_t lda, void *X,
                 const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ztbsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const nvpl_int_t K, const void *A, const nvpl_int_t lda,
                 void *X, const nvpl_int_t incX) NVPL_BLAS_API;
void cblas_ztpsv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE TransA, const enum CBLAS_DIAG Diag,
                 const nvpl_int_t N, const void *Ap, void *X, const nvpl_int_t incX) NVPL_BLAS_API;


/* 
 * Routines with S and D prefixes only
 */
void cblas_ssymv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const float alpha, const float *A,
                 const nvpl_int_t lda, const float *X, const nvpl_int_t incX,
                 const float beta, float *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_ssbmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const nvpl_int_t K, const float alpha, const float *A,
                 const nvpl_int_t lda, const float *X, const nvpl_int_t incX,
                 const float beta, float *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_sspmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const float alpha, const float *Ap,
                 const float *X, const nvpl_int_t incX,
                 const float beta, float *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_sger(const enum CBLAS_ORDER order, const nvpl_int_t M, const nvpl_int_t N,
                const float alpha, const float *X, const nvpl_int_t incX,
                const float *Y, const nvpl_int_t incY, float *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_ssyr(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const float alpha, const float *X,
                const nvpl_int_t incX, float *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_sspr(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const float alpha, const float *X,
                const nvpl_int_t incX, float *Ap) NVPL_BLAS_API;
void cblas_ssyr2(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const float alpha, const float *X,
                const nvpl_int_t incX, const float *Y, const nvpl_int_t incY, float *A,
                const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_sspr2(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const float alpha, const float *X,
                const nvpl_int_t incX, const float *Y, const nvpl_int_t incY, float *A) NVPL_BLAS_API;

void cblas_dsymv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const double alpha, const double *A,
                 const nvpl_int_t lda, const double *X, const nvpl_int_t incX,
                 const double beta, double *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_dsbmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const nvpl_int_t K, const double alpha, const double *A,
                 const nvpl_int_t lda, const double *X, const nvpl_int_t incX,
                 const double beta, double *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_dspmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const double alpha, const double *Ap,
                 const double *X, const nvpl_int_t incX,
                 const double beta, double *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_dger(const enum CBLAS_ORDER order, const nvpl_int_t M, const nvpl_int_t N,
                const double alpha, const double *X, const nvpl_int_t incX,
                const double *Y, const nvpl_int_t incY, double *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_dsyr(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const double alpha, const double *X,
                const nvpl_int_t incX, double *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_dspr(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const double alpha, const double *X,
                const nvpl_int_t incX, double *Ap) NVPL_BLAS_API;
void cblas_dsyr2(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const double alpha, const double *X,
                const nvpl_int_t incX, const double *Y, const nvpl_int_t incY, double *A,
                const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_dspr2(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const double alpha, const double *X,
                const nvpl_int_t incX, const double *Y, const nvpl_int_t incY, double *A) NVPL_BLAS_API;


/* 
 * Routines with C and Z prefixes only
 */
void cblas_chemv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const void *alpha, const void *A,
                 const nvpl_int_t lda, const void *X, const nvpl_int_t incX,
                 const void *beta, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_chbmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const nvpl_int_t K, const void *alpha, const void *A,
                 const nvpl_int_t lda, const void *X, const nvpl_int_t incX,
                 const void *beta, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_chpmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const void *alpha, const void *Ap,
                 const void *X, const nvpl_int_t incX,
                 const void *beta, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_cgeru(const enum CBLAS_ORDER order, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *X, const nvpl_int_t incX,
                 const void *Y, const nvpl_int_t incY, void *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_cgerc(const enum CBLAS_ORDER order, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *X, const nvpl_int_t incX,
                 const void *Y, const nvpl_int_t incY, void *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_cher(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const float alpha, const void *X, const nvpl_int_t incX,
                void *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_chpr(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const float alpha, const void *X,
                const nvpl_int_t incX, void *A) NVPL_BLAS_API;
void cblas_cher2(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo, const nvpl_int_t N,
                const void *alpha, const void *X, const nvpl_int_t incX,
                const void *Y, const nvpl_int_t incY, void *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_chpr2(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo, const nvpl_int_t N,
                const void *alpha, const void *X, const nvpl_int_t incX,
                const void *Y, const nvpl_int_t incY, void *Ap) NVPL_BLAS_API;

void cblas_zhemv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const void *alpha, const void *A,
                 const nvpl_int_t lda, const void *X, const nvpl_int_t incX,
                 const void *beta, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_zhbmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const nvpl_int_t K, const void *alpha, const void *A,
                 const nvpl_int_t lda, const void *X, const nvpl_int_t incX,
                 const void *beta, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_zhpmv(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                 const nvpl_int_t N, const void *alpha, const void *Ap,
                 const void *X, const nvpl_int_t incX,
                 const void *beta, void *Y, const nvpl_int_t incY) NVPL_BLAS_API;
void cblas_zgeru(const enum CBLAS_ORDER order, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *X, const nvpl_int_t incX,
                 const void *Y, const nvpl_int_t incY, void *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_zgerc(const enum CBLAS_ORDER order, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *X, const nvpl_int_t incX,
                 const void *Y, const nvpl_int_t incY, void *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_zher(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const double alpha, const void *X, const nvpl_int_t incX,
                void *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_zhpr(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo,
                const nvpl_int_t N, const double alpha, const void *X,
                const nvpl_int_t incX, void *A) NVPL_BLAS_API;
void cblas_zher2(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo, const nvpl_int_t N,
                const void *alpha, const void *X, const nvpl_int_t incX,
                const void *Y, const nvpl_int_t incY, void *A, const nvpl_int_t lda) NVPL_BLAS_API;
void cblas_zhpr2(const enum CBLAS_ORDER order, const enum CBLAS_UPLO Uplo, const nvpl_int_t N,
                const void *alpha, const void *X, const nvpl_int_t incX,
                const void *Y, const nvpl_int_t incY, void *Ap) NVPL_BLAS_API;

/*
 * ===========================================================================
 * Prototypes for level 3 BLAS
 * ===========================================================================
 */

/* 
 * Routines with standard 4 prefixes (S, D, C, Z)
 */
void cblas_sgemm(const enum CBLAS_ORDER Order, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_TRANSPOSE TransB, const nvpl_int_t M, const nvpl_int_t N,
                 const nvpl_int_t K, const float alpha, const float *A,
                 const nvpl_int_t lda, const float *B, const nvpl_int_t ldb,
                 const float beta, float *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_ssymm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const nvpl_int_t M, const nvpl_int_t N,
                 const float alpha, const float *A, const nvpl_int_t lda,
                 const float *B, const nvpl_int_t ldb, const float beta,
                 float *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_ssyrk(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                 const float alpha, const float *A, const nvpl_int_t lda,
                 const float beta, float *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_ssyr2k(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                  const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                  const float alpha, const float *A, const nvpl_int_t lda,
                  const float *B, const nvpl_int_t ldb, const float beta,
                  float *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_strmm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_DIAG Diag, const nvpl_int_t M, const nvpl_int_t N,
                 const float alpha, const float *A, const nvpl_int_t lda,
                 float *B, const nvpl_int_t ldb) NVPL_BLAS_API;
void cblas_strsm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_DIAG Diag, const nvpl_int_t M, const nvpl_int_t N,
                 const float alpha, const float *A, const nvpl_int_t lda,
                 float *B, const nvpl_int_t ldb) NVPL_BLAS_API;

void cblas_dgemm(const enum CBLAS_ORDER Order, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_TRANSPOSE TransB, const nvpl_int_t M, const nvpl_int_t N,
                 const nvpl_int_t K, const double alpha, const double *A,
                 const nvpl_int_t lda, const double *B, const nvpl_int_t ldb,
                 const double beta, double *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_dsymm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const nvpl_int_t M, const nvpl_int_t N,
                 const double alpha, const double *A, const nvpl_int_t lda,
                 const double *B, const nvpl_int_t ldb, const double beta,
                 double *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_dsyrk(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                 const double alpha, const double *A, const nvpl_int_t lda,
                 const double beta, double *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_dsyr2k(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                  const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                  const double alpha, const double *A, const nvpl_int_t lda,
                  const double *B, const nvpl_int_t ldb, const double beta,
                  double *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_dtrmm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_DIAG Diag, const nvpl_int_t M, const nvpl_int_t N,
                 const double alpha, const double *A, const nvpl_int_t lda,
                 double *B, const nvpl_int_t ldb) NVPL_BLAS_API;
void cblas_dtrsm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_DIAG Diag, const nvpl_int_t M, const nvpl_int_t N,
                 const double alpha, const double *A, const nvpl_int_t lda,
                 double *B, const nvpl_int_t ldb) NVPL_BLAS_API;

void cblas_cgemm(const enum CBLAS_ORDER Order, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_TRANSPOSE TransB, const nvpl_int_t M, const nvpl_int_t N,
                 const nvpl_int_t K, const void *alpha, const void *A,
                 const nvpl_int_t lda, const void *B, const nvpl_int_t ldb,
                 const void *beta, void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_csymm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 const void *B, const nvpl_int_t ldb, const void *beta,
                 void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_csyrk(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 const void *beta, void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_csyr2k(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                  const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                  const void *alpha, const void *A, const nvpl_int_t lda,
                  const void *B, const nvpl_int_t ldb, const void *beta,
                  void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_ctrmm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_DIAG Diag, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 void *B, const nvpl_int_t ldb) NVPL_BLAS_API;
void cblas_ctrsm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_DIAG Diag, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 void *B, const nvpl_int_t ldb) NVPL_BLAS_API;

void cblas_zgemm(const enum CBLAS_ORDER Order, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_TRANSPOSE TransB, const nvpl_int_t M, const nvpl_int_t N,
                 const nvpl_int_t K, const void *alpha, const void *A,
                 const nvpl_int_t lda, const void *B, const nvpl_int_t ldb,
                 const void *beta, void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_zsymm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 const void *B, const nvpl_int_t ldb, const void *beta,
                 void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_zsyrk(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 const void *beta, void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_zsyr2k(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                  const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                  const void *alpha, const void *A, const nvpl_int_t lda,
                  const void *B, const nvpl_int_t ldb, const void *beta,
                  void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_ztrmm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_DIAG Diag, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 void *B, const nvpl_int_t ldb) NVPL_BLAS_API;
void cblas_ztrsm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const enum CBLAS_TRANSPOSE TransA,
                 const enum CBLAS_DIAG Diag, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 void *B, const nvpl_int_t ldb) NVPL_BLAS_API;


/* 
 * Routines with prefixes C and Z only
 */
void cblas_chemm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 const void *B, const nvpl_int_t ldb, const void *beta,
                 void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_cherk(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                 const float alpha, const void *A, const nvpl_int_t lda,
                 const float beta, void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_cher2k(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                  const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                  const void *alpha, const void *A, const nvpl_int_t lda,
                  const void *B, const nvpl_int_t ldb, const float beta,
                  void *C, const nvpl_int_t ldc) NVPL_BLAS_API;

void cblas_zhemm(const enum CBLAS_ORDER Order, const enum CBLAS_SIDE Side,
                 const enum CBLAS_UPLO Uplo, const nvpl_int_t M, const nvpl_int_t N,
                 const void *alpha, const void *A, const nvpl_int_t lda,
                 const void *B, const nvpl_int_t ldb, const void *beta,
                 void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_zherk(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                 const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                 const double alpha, const void *A, const nvpl_int_t lda,
                 const double beta, void *C, const nvpl_int_t ldc) NVPL_BLAS_API;
void cblas_zher2k(const enum CBLAS_ORDER Order, const enum CBLAS_UPLO Uplo,
                  const enum CBLAS_TRANSPOSE Trans, const nvpl_int_t N, const nvpl_int_t K,
                  const void *alpha, const void *A, const nvpl_int_t lda,
                  const void *B, const nvpl_int_t ldb, const double beta,
                  void *C, const nvpl_int_t ldc) NVPL_BLAS_API;

/*
 * ===========================================================================
 * BLAS Extension prototypes
 * ===========================================================================
 */

// -- Batch APIs --

void cblas_sgemm_batch(enum CBLAS_ORDER Order,
                       enum CBLAS_TRANSPOSE *TransA_array,
                       enum CBLAS_TRANSPOSE *TransB_array,
                       nvpl_int_t *M_array, nvpl_int_t *N_array,
                       nvpl_int_t *K_array, const float *alpha_array,
                       const float  **A_array, nvpl_int_t *lda_array,
                       const float  **B_array, nvpl_int_t *ldb_array,
                       const float *beta_array,
                       float  **C_array, nvpl_int_t *ldc_array,
                       nvpl_int_t group_count, nvpl_int_t *group_size) NVPL_BLAS_API;
void cblas_dgemm_batch(enum CBLAS_ORDER Order,
                       enum CBLAS_TRANSPOSE *TransA_array,
                       enum CBLAS_TRANSPOSE *TransB_array,
                       nvpl_int_t *M_array, nvpl_int_t *N_array,
                       nvpl_int_t *K_array, const double *alpha_array,
                       const double  **A_array, nvpl_int_t *lda_array,
                       const double  **B_array, nvpl_int_t *ldb_array,
                       const double *beta_array,
                       double **C_array, nvpl_int_t *ldc_array,
                       nvpl_int_t group_count, nvpl_int_t *group_size) NVPL_BLAS_API;
void cblas_cgemm_batch(enum CBLAS_ORDER Order,
                       enum CBLAS_TRANSPOSE *TransA_array,
                       enum CBLAS_TRANSPOSE *TransB_array,
                       nvpl_int_t *M_array, nvpl_int_t *N_array,
                       nvpl_int_t *K_array, const void *alpha_array,
                       const void  **A_array, nvpl_int_t *lda_array,
                       const void  **B_array, nvpl_int_t *ldb_array,
                       const void *beta_array,
                       void **C_array, nvpl_int_t *ldc_array,
                       nvpl_int_t group_count, nvpl_int_t *group_size) NVPL_BLAS_API;
void cblas_zgemm_batch(enum CBLAS_ORDER Order,
                       enum CBLAS_TRANSPOSE *TransA_array,
                       enum CBLAS_TRANSPOSE *TransB_array,
                       nvpl_int_t *M_array, nvpl_int_t *N_array,
                       nvpl_int_t *K_array, const void *alpha_array,
                       const void  **A_array, nvpl_int_t *lda_array,
                       const void  **B_array, nvpl_int_t *ldb_array,
                       const void *beta_array,
                       void **C_array, nvpl_int_t *ldc_array,
                       nvpl_int_t group_count, nvpl_int_t *group_size) NVPL_BLAS_API;

void cblas_sgemm_batch_strided(const enum CBLAS_ORDER Order,
                               const enum CBLAS_TRANSPOSE TransA,
                               const enum CBLAS_TRANSPOSE TransB,
                               const nvpl_int_t M,
                               const nvpl_int_t N,
                               const nvpl_int_t K,
                               const float alpha,
                               const float *A, const nvpl_int_t lda, const nvpl_int_t stridea,
                               const float *B, const nvpl_int_t ldb, const nvpl_int_t strideb,
                               const float beta,
                               float *C, const nvpl_int_t ldc, const nvpl_int_t stridec,
                               const nvpl_int_t batch_size) NVPL_BLAS_API;
void cblas_dgemm_batch_strided(const enum CBLAS_ORDER Order,
                               const enum CBLAS_TRANSPOSE TransA,
                               const enum CBLAS_TRANSPOSE TransB,
                               const nvpl_int_t M,
                               const nvpl_int_t N,
                               const nvpl_int_t K,
                               const double alpha,
                               const double *A, const nvpl_int_t lda, const nvpl_int_t stridea,
                               const double *B, const nvpl_int_t ldb, const nvpl_int_t strideb,
                               const double beta,
                               double *C, const nvpl_int_t ldc, const nvpl_int_t stridec,
                               const nvpl_int_t batch_size) NVPL_BLAS_API;
void cblas_cgemm_batch_strided(const enum CBLAS_ORDER Order,
                               const enum CBLAS_TRANSPOSE TransA,
                               const enum CBLAS_TRANSPOSE TransB,
                               const nvpl_int_t M,
                               const nvpl_int_t N,
                               const nvpl_int_t K,
                               const void *alpha,
                               const void *A, const nvpl_int_t lda, const nvpl_int_t stridea,
                               const void *B, const nvpl_int_t ldb, const nvpl_int_t strideb,
                               const void *beta,
                               void *C, const nvpl_int_t ldc, const nvpl_int_t stridec,
                               const nvpl_int_t batch_size) NVPL_BLAS_API;
void cblas_zgemm_batch_strided(const enum CBLAS_ORDER Order,
                               const enum CBLAS_TRANSPOSE TransA,
                               const enum CBLAS_TRANSPOSE TransB,
                               const nvpl_int_t M,
                               const nvpl_int_t N,
                               const nvpl_int_t K,
                               const void *alpha,
                               const void *A, const nvpl_int_t lda, const nvpl_int_t stridea,
                               const void *B, const nvpl_int_t ldb, const nvpl_int_t strideb,
                               const void *beta,
                               void *C, const nvpl_int_t ldc, const nvpl_int_t stridec,
                               const nvpl_int_t batch_size) NVPL_BLAS_API;

#ifdef __cplusplus
}
#endif
#endif
