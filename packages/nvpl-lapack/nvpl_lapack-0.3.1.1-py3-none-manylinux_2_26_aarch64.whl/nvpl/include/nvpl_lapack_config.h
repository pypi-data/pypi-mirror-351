#ifndef NVPL_LAPACK_CONFIG_H
#define NVPL_LAPACK_CONFIG_H

#ifdef __cplusplus
#if defined(NVPL_LAPACK_COMPLEX_CPP)
#include <complex>
#endif
extern "C" {
#endif /* __cplusplus */

#include <inttypes.h>
#include <stdint.h>
#include <stdlib.h>

typedef int64_t nvpl_int64_t;
typedef int32_t nvpl_int32_t;

#ifndef nvpl_int_t
#if defined(NVPL_ILP64)
#define nvpl_int_t nvpl_int64_t
#else
#define nvpl_int_t nvpl_int32_t
#endif
#endif

/*
 * Integer format string
 */
#ifndef NVPL_LAPACK_IFMT
#if defined(NVPL_ILP64)
#define NVPL_LAPACK_IFMT PRId64
#else
#define NVPL_LAPACK_IFMT PRId32
#endif
#endif

#ifndef nvpl_lapack_logical
#define nvpl_lapack_logical nvpl_int_t
#endif

#ifndef NVPL_LAPACK_COMPLEX_CUSTOM

#if defined(NVPL_LAPACK_COMPLEX_STRUCTURE)

typedef struct {
    float real, imag;
} _nvpl_scomplex_t;
typedef struct {
    double real, imag;
} _nvpl_dcomplex_t;
#define nvpl_scomplex_t _nvpl_scomplex_t
#define nvpl_dcomplex_t _nvpl_dcomplex_t
#define nvpl_scomplex_t_real(z) ((z).real)
#define nvpl_scomplex_t_imag(z) ((z).imag)
#define nvpl_dcomplex_t_real(z) ((z).real)
#define nvpl_dcomplex_t_imag(z) ((z).imag)

#elif defined(NVPL_LAPACK_COMPLEX_C99)

#include <complex.h>
#define nvpl_scomplex_t float _Complex
#define nvpl_dcomplex_t double _Complex
#define nvpl_scomplex_t_real(z) (creal(z))
#define nvpl_scomplex_t_imag(z) (cimag(z))
#define nvpl_dcomplex_t_real(z) (creal(z))
#define nvpl_dcomplex_t_imag(z) (cimag(z))

#elif defined(NVPL_LAPACK_COMPLEX_CPP)

#define nvpl_scomplex_t std::complex<float>
#define nvpl_dcomplex_t std::complex<double>
#define nvpl_scomplex_t_real(z) ((z).real())
#define nvpl_scomplex_t_imag(z) ((z).imag())
#define nvpl_dcomplex_t_real(z) ((z).real())
#define nvpl_dcomplex_t_imag(z) ((z).imag())

#else

#include <complex.h>
#define nvpl_scomplex_t float _Complex
#define nvpl_dcomplex_t double _Complex
#define nvpl_scomplex_t_real(z) (creal(z))
#define nvpl_scomplex_t_imag(z) (cimag(z))
#define nvpl_dcomplex_t_real(z) (creal(z))
#define nvpl_dcomplex_t_imag(z) (cimag(z))

#endif

#endif

#ifndef NVPL_LAPACK_malloc
#define NVPL_LAPACK_malloc(size) malloc(size)
#endif

#ifndef NVPL_LAPACK_free
#define NVPL_LAPACK_free(p) free(p)
#endif

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* NVPL_LAPACK_CONFIG_H */
