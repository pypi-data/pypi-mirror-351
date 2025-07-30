#ifndef NVPL_LAPACK_TYPES_H
#define NVPL_LAPACK_TYPES_H

/* Math mode
 *
 * NVPL_LAPACK_MATH_MODE_PEDANTIC: highest numerical robustness, might results in worse performance
 * NVPL_LAPACK_MATH_MODE_DEFAULT: trade-off between numerical robustness and performance
 * NVPL_LAPACK_MATH_MODE_USE_GLOBAL: reset local thread setting and use global mode
 *
 * Directly affected routines: LARFG
 *
 * Note that some routines are affected implicitly by using one of the listed routines above.
 *
 */
typedef enum {
    NVPL_LAPACK_MATH_MODE_DEFAULT = 0,
    NVPL_LAPACK_MATH_MODE_PEDANTIC = 1,
    NVPL_LAPACK_MATH_MODE_USE_GLOBAL = 2
} nvpl_lapack_math_mode_t;

/* Environment variable mode
 *
 * NVPL_LAPACK_ENV_MODE_IGNORE: ignore NVPL LAPACK specific environment variables
 * NVPL_LAPACK_ENV_MODE_DEFAULT: respect NVPL LAPACK specific environment variables
 * NVPL_LAPACK_ENV_MODE_USE_GLOBAL: reset local thread setting and use global mode
 *
 */
typedef enum {
    NVPL_LAPACK_ENV_MODE_DEFAULT = 0,
    NVPL_LAPACK_ENV_MODE_IGNORE = 1,
    NVPL_LAPACK_ENV_MODE_USE_GLOBAL = 2
} nvpl_lapack_env_mode_t;
#endif
