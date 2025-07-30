 /* Copyright 2005-2023 NVIDIA Corporation.  All rights reserved.
  *
  * NOTICE TO LICENSEE:
  *
  * The source code and/or documentation ("Licensed Deliverables") are
  * subject to NVIDIA intellectual property rights under U.S. and
  * international Copyright laws.
  *
  * The Licensed Deliverables contained herein are PROPRIETARY and
  * CONFIDENTIAL to NVIDIA and are being provided under the terms and
  * conditions of a form of NVIDIA software license agreement by and
  * between NVIDIA and Licensee ("License Agreement") or electronically
  * accepted by Licensee.  Notwithstanding any terms or conditions to
  * the contrary in the License Agreement, reproduction or disclosure
  * of the Licensed Deliverables to any third party without the express
  * written consent of NVIDIA is prohibited.
  *
  * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
  * LICENSE AGREEMENT, NVIDIA MAKES NO REPRESENTATION ABOUT THE
  * SUITABILITY OF THESE LICENSED DELIVERABLES FOR ANY PURPOSE.  THEY ARE
  * PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND.
  * NVIDIA DISCLAIMS ALL WARRANTIES WITH REGARD TO THESE LICENSED
  * DELIVERABLES, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY,
  * NONINFRINGEMENT, AND FITNESS FOR A PARTICULAR PURPOSE.
  * NOTWITHSTANDING ANY TERMS OR CONDITIONS TO THE CONTRARY IN THE
  * LICENSE AGREEMENT, IN NO EVENT SHALL NVIDIA BE LIABLE FOR ANY
  * SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, OR ANY
  * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
  * WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
  * ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
  * OF THESE LICENSED DELIVERABLES.
  *
  * U.S. Government End Users.  These Licensed Deliverables are a
  * "commercial item" as that term is defined at 48 C.F.R. 2.101 (OCT
  * 1995), consisting of "commercial computer software" and "commercial
  * computer software documentation" as such terms are used in 48
  * C.F.R. 12.212 (SEPT 1995) and are provided to the U.S. Government
  * only as a commercial end item.  Consistent with 48 C.F.R.12.212 and
  * 48 C.F.R. 227.7202-1 through 227.7202-4 (JUNE 1995), all
  * U.S. Government End Users acquire the Licensed Deliverables with
  * only those rights set forth herein.
  *
  * Any use of the Licensed Deliverables in individual and commercial
  * software must include, in the user documentation and internal
  * comments to the code, the above Disclaimer and U.S. Government End
  * Users Notice.
  */

/*!
* \file nvpl_fftw.h
* \brief Public header file for the NVIDIA NVPL FFTW library (NVPL_FFTW)
*/

#ifndef _NVPL_FFTW_H_
#define _NVPL_FFTW_H_

#include "nvpl_fft_version.h"

#include <stdio.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Transform direction
#define FFTW_FORWARD (-1)
#define FFTW_INVERSE  (1)
#define FFTW_BACKWARD (1)

#define FFTW_NO_TIMELIMIT (-1.0)

// Documented flags
#define FFTW_MEASURE         (0U)
#define FFTW_DESTROY_INPUT   (1U << 0)
#define FFTW_UNALIGNED       (1U << 1)
#define FFTW_CONSERVE_MEMORY (1U << 2)
#define FFTW_EXHAUSTIVE      (1U << 3)
#define FFTW_PRESERVE_INPUT  (1U << 4)
#define FFTW_PATIENT         (1U << 5)
#define FFTW_ESTIMATE        (1U << 6)
#define FFTW_WISDOM_ONLY     (1U << 21)

// Undocumented beyond-guru flags
#define FFTW_ESTIMATE_PATIENT       (1U << 7)
#define FFTW_BELIEVE_PCOST          (1U << 8)
#define FFTW_NO_DFT_R2HC            (1U << 9)
#define FFTW_NO_NONTHREADED         (1U << 10)
#define FFTW_NO_BUFFERING           (1U << 11)
#define FFTW_NO_INDIRECT_OP         (1U << 12)
#define FFTW_ALLOW_LARGE_GENERIC    (1U << 13)
#define FFTW_NO_RANK_SPLITS         (1U << 14)
#define FFTW_NO_VRANK_SPLITS        (1U << 15)
#define FFTW_NO_VRECURSE            (1U << 16)
#define FFTW_NO_SIMD                (1U << 17)
#define FFTW_NO_SLOW                (1U << 18)
#define FFTW_NO_FIXED_RADIX_LARGE_N (1U << 19)
#define FFTW_ALLOW_PRUNING          (1U << 20)

// NVPL_FFTW defines and supports the following data types

// Note if complex.h has been included we use the C99 complex types
#if !defined(FFTW_NO_Complex) && defined(_Complex_I) && defined (complex)
  typedef double _Complex fftw_complex;
  typedef float _Complex fftwf_complex;
#else
  typedef double fftw_complex[2];
  typedef float fftwf_complex[2];
#endif

typedef void *fftw_plan;

typedef void *fftwf_plan;

typedef struct {
  int n;
  int is;
  int os;
} fftw_iodim;

typedef fftw_iodim fftwf_iodim;

typedef struct {
  ptrdiff_t n;
  ptrdiff_t is;
  ptrdiff_t os;
} fftw_iodim64;

typedef fftw_iodim64 fftwf_iodim64;

#ifndef NVPLFFTAPI
#ifdef _WIN32
#define NVPLFFTAPI __stdcall
#elif __GNUC__ >= 4
#define NVPLFFTAPI __attribute__ ((visibility ("default")))
#else
#define NVPLFFTAPI
#endif
#endif

#ifdef _WIN32
#define _NVPLFFTAPI(T) T NVPLFFTAPI
#else
#define _NVPLFFTAPI(T) NVPLFFTAPI T
#endif

// Utility functions

int NVPLFFTAPI nvpl_fft_get_version(void);

// NVPL_FFTW defines and supports the following double precision APIs

fftw_plan NVPLFFTAPI fftw_plan_dft_1d(int n0,
                                      fftw_complex *in,
                                      fftw_complex *out,
                                      int sign,
                                      unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_2d(int n0,
                                      int n1,
                                      fftw_complex *in,
                                      fftw_complex *out,
                                      int sign,
                                      unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_3d(int n0,
                                      int n1,
                                      int n2,
                                      fftw_complex *in,
                                      fftw_complex *out,
                                      int sign,
                                      unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft(int rank,
                                   const int *n,
                                   fftw_complex *in,
                                   fftw_complex *out,
                                   int sign,
                                   unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_r2c_1d(int n,
                                          double *in,
                                          fftw_complex *out,
                                          unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_r2c_2d(int n0,
                                          int n1,
                                          double *in,
                                          fftw_complex *out,
                                          unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_r2c_3d(int n0,
                                          int n1,
                                          int n2,
                                          double *in,
                                          fftw_complex *out,
                                          unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_r2c(int rank,
                                       const int *n,
                                       double *in,
                                       fftw_complex *out,
                                       unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_c2r_1d(int n0,
                                          fftw_complex *in,
                                          double *out,
                                          unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_c2r_2d(int n0,
                                          int n1,
                                          fftw_complex *in,
                                          double *out,
                                          unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_c2r_3d(int n0,
                                          int n1,
                                          int n2,
                                          fftw_complex *in,
                                          double *out,
                                          unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_dft_c2r(int rank,
                                       const int *n,
                                       fftw_complex *in,
                                       double *out,
                                       unsigned flags);


fftw_plan NVPLFFTAPI fftw_plan_many_dft(int rank,
                                        const int *n,
                                        int batch,
                                        fftw_complex *in,
                                        const int *inembed, int istride, int idist,
                                        fftw_complex *out,
                                        const int *onembed, int ostride, int odist,
                                        int sign, unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_many_dft_r2c(int rank,
                                            const int *n,
                                            int batch,
                                            double *in,
                                            const int *inembed, int istride, int idist,
                                            fftw_complex *out,
                                            const int *onembed, int ostride, int odist,
                                            unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_many_dft_c2r(int rank,
                                            const int *n,
                                            int batch,
                                            fftw_complex *in,
                                            const int *inembed, int istride, int idist,
                                            double *out,
                                            const int *onembed, int ostride, int odist,
                                            unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_guru_dft(int rank, const fftw_iodim *dims,
                                        int batch_rank, const fftw_iodim *batch_dims,
                                        fftw_complex *in, fftw_complex *out,
                                        int sign, unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_guru_dft_r2c(int rank, const fftw_iodim *dims,
                                            int batch_rank, const fftw_iodim *batch_dims,
                                            double *in, fftw_complex *out,
                                            unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_guru_dft_c2r(int rank, const fftw_iodim *dims,
                                            int batch_rank, const fftw_iodim *batch_dims,
                                            fftw_complex *in, double *out,
                                            unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_guru64_dft(int rank, const fftw_iodim64* dims,
                                          int batch_rank, const fftw_iodim64* batch_dims,
                                          fftw_complex* in, fftw_complex* out, int sign,
                                          unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_guru64_dft_r2c(int rank, const fftw_iodim64* dims,
                                              int batch_rank, const fftw_iodim64* batch_dims,
                                              double* in, fftw_complex* out,
                                              unsigned flags);

fftw_plan NVPLFFTAPI fftw_plan_guru64_dft_c2r(int rank, const fftw_iodim64* dims,
                                              int batch_rank, const fftw_iodim64* batch_dims,
                                              fftw_complex* in, double* out,
                                              unsigned flags);

void NVPLFFTAPI fftw_execute(const fftw_plan plan);

void NVPLFFTAPI fftw_execute_dft(const fftw_plan plan,
                                 fftw_complex *idata,
                                 fftw_complex *odata);

void NVPLFFTAPI fftw_execute_dft_r2c(const fftw_plan plan,
                                     double *idata,
                                     fftw_complex *odata);

void NVPLFFTAPI fftw_execute_dft_c2r(const fftw_plan plan,
                                     fftw_complex *idata,
                                     double *odata);

// NVPL_FFTW defines and supports the following single precision APIs

fftwf_plan NVPLFFTAPI fftwf_plan_dft_1d(int n0,
                                        fftwf_complex *in,
                                        fftwf_complex *out,
                                        int sign,
                                        unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_2d(int n0,
                                        int n1,
                                        fftwf_complex *in,
                                        fftwf_complex *out,
                                        int sign,
                                        unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_3d(int n0,
                                        int n1,
                                        int n2,
                                        fftwf_complex *in,
                                        fftwf_complex *out,
                                        int sign,
                                        unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft(int rank,
                                     const int *n,
                                     fftwf_complex *in,
                                     fftwf_complex *out,
                                     int sign,
                                     unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_r2c_1d(int n0,
                                            float *in,
                                            fftwf_complex *out,
                                            unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_r2c_2d(int n0,
                                            int n1,
                                            float *in,
                                            fftwf_complex *out,
                                            unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_r2c_3d(int n0,
                                            int n1,
                                            int n2,
                                            float *in,
                                            fftwf_complex *out,
                                            unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_r2c(int rank,
                                         const int *n,
                                         float *in,
                                         fftwf_complex *out,
                                         unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_c2r_1d(int n0,
                                            fftwf_complex *in,
                                            float *out,
                                            unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_c2r_2d(int n0,
                                            int n1,
                                            fftwf_complex *in,
                                            float *out,
                                            unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_c2r_3d(int n0,
                                            int n1,
                                            int n2,
                                            fftwf_complex *in,
                                            float *out,
                                            unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_dft_c2r(int rank,
                                         const int *n,
                                         fftwf_complex *in,
                                         float *out,
                                         unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_many_dft(int rank,
                                          const int *n,
                                          int batch,
                                          fftwf_complex *in,
                                          const int *inembed, int istride, int idist,
                                          fftwf_complex *out,
                                          const int *onembed, int ostride, int odist,
                                          int sign, unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_many_dft_r2c(int rank,
                                              const int *n,
                                              int batch,
                                              float *in,
                                              const int *inembed, int istride, int idist,
                                              fftwf_complex *out,
                                              const int *onembed, int ostride, int odist,
                                              unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_many_dft_c2r(int rank,
                                              const int *n,
                                              int batch,
                                              fftwf_complex *in,
                                              const int *inembed, int istride, int idist,
                                              float *out,
                                              const int *onembed, int ostride, int odist,
                                              unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_guru_dft(int rank, const fftwf_iodim *dims,
                                          int batch_rank, const fftwf_iodim *batch_dims,
                                          fftwf_complex *in, fftwf_complex *out,
                                          int sign, unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_guru_dft_r2c(int rank, const fftwf_iodim *dims,
                                              int batch_rank, const fftwf_iodim *batch_dims,
                                              float *in, fftwf_complex *out,
                                              unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_guru_dft_c2r(int rank, const fftwf_iodim *dims,
                                              int batch_rank, const fftwf_iodim *batch_dims,
                                              fftwf_complex *in, float *out,
                                              unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_guru64_dft(int rank, const fftwf_iodim64* dims,
                                            int batch_rank, const fftwf_iodim64* batch_dims,
                                            fftwf_complex* in, fftwf_complex* out, int sign,
                                             unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_guru64_dft_r2c(int rank, const fftwf_iodim64* dims,
                                                int batch_rank, const fftwf_iodim64* batch_dims,
                                                float* in, fftwf_complex* out,
                                                unsigned flags);

fftwf_plan NVPLFFTAPI fftwf_plan_guru64_dft_c2r(int rank, const fftwf_iodim64* dims,
                                                int batch_rank, const fftwf_iodim64* batch_dims,
                                                fftwf_complex* in, float* out,
                                                unsigned flags);

void NVPLFFTAPI fftwf_execute(const fftw_plan plan);

void NVPLFFTAPI fftwf_execute_dft(const fftwf_plan plan,
                                  fftwf_complex *idata,
                                  fftwf_complex *odata);

void NVPLFFTAPI fftwf_execute_dft_r2c(const fftwf_plan plan,
                                      float *idata,
                                      fftwf_complex *odata);

void NVPLFFTAPI fftwf_execute_dft_c2r(const fftwf_plan plan,
                                      fftwf_complex *idata,
                                      float *odata);

// NVPL_FFTW defines and supports the following thread control APIs

int NVPLFFTAPI fftw_init_threads(void);

int NVPLFFTAPI fftwf_init_threads(void);

void NVPLFFTAPI fftw_plan_with_nthreads(int nthreads);

void NVPLFFTAPI fftwf_plan_with_nthreads(int nthreads);

int NVPLFFTAPI fftw_planner_nthreads(void);

int NVPLFFTAPI fftwf_planner_nthreads(void);

void NVPLFFTAPI fftw_cleanup_threads(void);

void NVPLFFTAPI fftwf_cleanup_threads(void);

// NVPL_FFTW defines and supports the following support APIs

_NVPLFFTAPI(void *) fftw_malloc(size_t n);

_NVPLFFTAPI(void *) fftwf_malloc(size_t n);

_NVPLFFTAPI(double *) fftw_alloc_real(size_t n);

_NVPLFFTAPI(fftw_complex *) fftw_alloc_complex(size_t n);

_NVPLFFTAPI(float *) fftwf_alloc_real(size_t n);

_NVPLFFTAPI(fftwf_complex *) fftwf_alloc_complex(size_t n);

int NVPLFFTAPI fftw_alignment_of(double *p);

int NVPLFFTAPI fftwf_alignment_of(float *p);

void NVPLFFTAPI fftw_free(void *pointer);

void NVPLFFTAPI fftwf_free(void *pointer);

int NVPLFFTAPI fftw_import_system_wisdom(void);

int NVPLFFTAPI fftwf_import_system_wisdom(void);

void NVPLFFTAPI fftw_export_wisdom(void (*write_char)(char c, void *), void *data);

void NVPLFFTAPI fftwf_export_wisdom(void (*write_char)(char c, void *), void *data);

int NVPLFFTAPI fftw_import_wisdom(int (*read_char)(void *), void *data);

int NVPLFFTAPI fftwf_import_wisdom(int (*read_char)(void *), void *data);

void NVPLFFTAPI fftw_export_wisdom_to_file(FILE * output_file);

void NVPLFFTAPI fftwf_export_wisdom_to_file(FILE * output_file);

int NVPLFFTAPI fftw_import_wisdom_from_file(FILE * input_file);

int NVPLFFTAPI fftwf_import_wisdom_from_file(FILE * input_file);

_NVPLFFTAPI(char*) fftw_export_wisdom_to_string(void);

_NVPLFFTAPI(char*) fftwf_export_wisdom_to_string(void);

int NVPLFFTAPI fftw_import_wisdom_from_string(const char *input_string);

int NVPLFFTAPI fftwf_import_wisdom_from_string(const char *input_string);

void fftw_forget_wisdom(void);

void fftwf_forget_wisdom(void);

void NVPLFFTAPI fftw_print_plan(const fftw_plan plan);

void NVPLFFTAPI fftwf_print_plan(const fftwf_plan plan);

void NVPLFFTAPI fftw_set_timelimit(double seconds);

void NVPLFFTAPI fftwf_set_timelimit(double seconds);

double NVPLFFTAPI fftw_cost(const fftw_plan plan);

double NVPLFFTAPI fftwf_cost(const fftw_plan plan);

void NVPLFFTAPI fftw_flops(const fftw_plan plan, double *add, double *mul, double *fma);

void NVPLFFTAPI fftwf_flops(const fftw_plan plan, double *add, double *mul, double *fma);

void NVPLFFTAPI fftw_destroy_plan(fftw_plan plan);

void NVPLFFTAPI fftwf_destroy_plan(fftwf_plan plan);

void NVPLFFTAPI fftw_cleanup(void);

void NVPLFFTAPI fftwf_cleanup(void);

#ifdef __cplusplus
}
#endif

#endif /* _NVPL_FFTW_H_ */
