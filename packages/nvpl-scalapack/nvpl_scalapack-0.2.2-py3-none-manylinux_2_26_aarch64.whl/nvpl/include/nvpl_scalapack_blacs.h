// Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto.  Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.

#ifndef NVPL_SCALAPACK_BLACS_H
#define NVPL_SCALAPACK_BLACS_H

#include "nvpl_scalapack_types.h"

#ifdef __cplusplus
extern "C" {
#endif

///
/// comm support
///
void blacs_pinfo_(nvpl_int_t *mpi_rank, nvpl_int_t *mpi_size);
void blacs_exit_(nvpl_int_t *keep_mpi);

void blacs_gridinit_(nvpl_int_t *icontxt, char *grid_layout, nvpl_int_t *nprow, nvpl_int_t *npcol);
void blacs_gridexit_(nvpl_int_t *icontxt);

void blacs_set_(nvpl_int_t *icontxt, nvpl_int_t *what, nvpl_int_t *val);
void blacs_get_(nvpl_int_t *icontxt, nvpl_int_t *what, nvpl_int_t *val);
void blacs_setup_(nvpl_int_t *mpi_rank, nvpl_int_t *mpi_size);

void blacs_gridmap_(nvpl_int_t *icontxt, nvpl_int_t *usermap, nvpl_int_t *ldup, nvpl_int_t *nprow0, nvpl_int_t *npcol0);
void blacs_gridinfo_(nvpl_int_t *icontxt, nvpl_int_t *nprow, nvpl_int_t *npcol, nvpl_int_t *myrow, nvpl_int_t *mycol);

void blacs_barrier_(nvpl_int_t *icontxt, char *scope);

nvpl_int_t blacs_pnum_(nvpl_int_t *icontxt, nvpl_int_t *prow, nvpl_int_t *pcol);
void blacs_pcoord_(nvpl_int_t *icontxt, nvpl_int_t *nodenum, nvpl_int_t *prow, nvpl_int_t *pcol);

void blacs_freebuff_(nvpl_int_t *icontxt, nvpl_int_t *wait);
void blacs_abort_(nvpl_int_t *icontxt, nvpl_int_t *ierr);

///
/// distribution
///
void igamx2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              nvpl_int_t *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void sgamx2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void dgamx2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void cgamx2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void zgamx2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);

void igamn2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              nvpl_int_t *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void sgamn2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void dgamn2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void cgamn2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void zgamn2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, nvpl_int_t *rA, nvpl_int_t *cA, const nvpl_int_t *ldia,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);

void igsum2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              nvpl_int_t *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void sgsum2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void dgsum2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void cgsum2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void zgsum2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);

void igesd2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, nvpl_int_t *A, const nvpl_int_t *lda,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void sgesd2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, float *A, const nvpl_int_t *lda,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void dgesd2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, double *A, const nvpl_int_t *lda,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void cgesd2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, float *A, const nvpl_int_t *lda,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void zgesd2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, double *A, const nvpl_int_t *lda,
              const nvpl_int_t *rdest, const nvpl_int_t *cdest);

void itrsd2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              const nvpl_int_t *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void strsd2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              const float *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void dtrsd2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              const double *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void ctrsd2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              const float *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);
void ztrsd2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              const double *A, const nvpl_int_t *lda, const nvpl_int_t *rdest, const nvpl_int_t *cdest);

void igerv2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, nvpl_int_t *A, const nvpl_int_t *lda,
              const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void sgerv2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, float *A, const nvpl_int_t *lda,
              const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void dgerv2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, double *A, const nvpl_int_t *lda,
              const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void cgerv2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, float *A, const nvpl_int_t *lda,
              const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void zgerv2d_(const nvpl_int_t *icontxt, const nvpl_int_t *m, const nvpl_int_t *n, double *A, const nvpl_int_t *lda,
              const nvpl_int_t *rsrc, const nvpl_int_t *csrc);

void itrrv2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              nvpl_int_t *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void strrv2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void dtrrv2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void ctrrv2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void ztrrv2d_(const nvpl_int_t *icontxt, const char *uplo, const char *diag, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);

void igebs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              const nvpl_int_t *A, const nvpl_int_t *lda);
void sgebs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              const float *A, const nvpl_int_t *lda);
void dgebs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              const double *A, const nvpl_int_t *lda);
void cgebs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              const float *A, const nvpl_int_t *lda);
void zgebs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              const double *A, const nvpl_int_t *lda);

void itrbs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, const nvpl_int_t *A, const nvpl_int_t *lda);
void strbs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, const float *A, const nvpl_int_t *lda);
void dtrbs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, const double *A, const nvpl_int_t *lda);
void ctrbs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, const float *A, const nvpl_int_t *lda);
void ztrbs2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, const double *A, const nvpl_int_t *lda);

void igebr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              nvpl_int_t *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void sgebr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void dgebr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void cgebr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              float *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);
void zgebr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const nvpl_int_t *m, const nvpl_int_t *n,
              double *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc, const nvpl_int_t *csrc);

void itrbr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, nvpl_int_t *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc,
              const nvpl_int_t *csrc);
void strbr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, float *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc,
              const nvpl_int_t *csrc);
void dtrbr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, double *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc,
              const nvpl_int_t *csrc);
void ctrbr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, float *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc,
              const nvpl_int_t *csrc);
void ztrbr2d_(const nvpl_int_t *icontxt, const char *scope, const char *top, const char *uplo, const char *diag,
              const nvpl_int_t *m, const nvpl_int_t *n, double *A, const nvpl_int_t *lda, const nvpl_int_t *rsrc,
              const nvpl_int_t *csrc);

#ifdef __cplusplus
}
#endif

#endif /* NVPL_SCALAPACK_BLACS_H */
