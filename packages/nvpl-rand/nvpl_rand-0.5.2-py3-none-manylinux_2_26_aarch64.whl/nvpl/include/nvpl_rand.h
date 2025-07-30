#ifndef NVPL_RAND_H
#define NVPL_RAND_H

#include "nvpl_rand_version.h"
#include <stdint.h> // NOLINT
#include <stdio.h>  // NOLINT
#include <stddef.h> // NOLINT

/* \cond PRIVATE */
#ifndef NVPL_RAND_API
#    if __GNUC__ >= 4
#        define NVPL_RAND_API __attribute__((visibility("default")))
#    else
#        define NVPL_RAND_API
#    endif
#endif

#ifdef __cplusplus
#    ifndef NVPL_RAND_NOEXCEPT
#        define NVPL_RAND_NOEXCEPT noexcept
#    endif
#else
#    define NVPL_RAND_NOEXCEPT
#endif
/* \endcond */

/**
 * \defgroup NVPL RAND C API
 *
 * @{
 */
#ifdef __cplusplus
extern "C" {
#endif

/**
 * \brief NVPL RAND generator types.
*/
typedef enum nvplRandRngType // NOLINT: allow typedef in C header
{
    NVPL_RAND_RNG_PSEUDO_DEFAULT          = 100, ///< Default pseudorandom generator, same as NVPL_RAND_RNG_PSEUDO_XORWOW
    NVPL_RAND_RNG_PSEUDO_XORWOW           = 100, ///< XORWOW pseudorandom generator
    NVPL_RAND_RNG_PSEUDO_MRG32K3A         = 101, ///< MRG32K3A pseudorandom generator
    NVPL_RAND_RNG_PSEUDO_MT19937          = 102, ///< Mersenne Twister MT19937 pseudorandom generator
    NVPL_RAND_RNG_PSEUDO_PHILOX4_32_10    = 103, ///< PHILOX-4x32-10 pseudorandom generator
    NVPL_RAND_RNG_PSEUDO_PCG              = 104, ///< PCG pseudorandom generator
    NVPL_RAND_RNG_QUASI_DEFAULT           = 200, ///< Default quasirandom generator, same as NVPL_RAND_RNG_QUASI_SOBOL32
    NVPL_RAND_RNG_QUASI_SOBOL32           = 200, ///< SOBOL32 quasirandom generator
    NVPL_RAND_RNG_QUASI_SCRAMBLED_SOBOL32 = 201, ///< Scrambled SOBOL32 quasirandom generator
    NVPL_RAND_RNG_QUASI_SOBOL64           = 202, ///< SOBOL64 quasirandom generator
    NVPL_RAND_RNG_QUASI_SCRAMBLED_SOBOL64 = 203  ///< Scrambled SOBOL64 quasirandom generator
} nvplRandRngType_t;

/**
 * \brief NVPL RAND distribution types.
*/
typedef enum nvplRandDistributionType // NOLINT: allow typedef in C header
{
    // Uni-variate Continuous
    NVPL_RAND_CONTINUOUS_DIST_UNIFORM       = 101, ///< <a href="https://en.wikipedia.org/wiki/Continuous_uniform_distribution">Uniform distribution</a> with range (0,1].
    NVPL_RAND_CONTINUOUS_DIST_UNIFORM_RANGE = 102, ///< <a href="https://en.wikipedia.org/wiki/Continuous_uniform_distribution">Uniform distribution</a> with custom range.
    NVPL_RAND_CONTINUOUS_DIST_NORMAL        = 103, ///< <a href="https://en.wikipedia.org/wiki/Normal_distribution">Normal distribution</a>.
    NVPL_RAND_CONTINUOUS_DIST_LOGNORMAL     = 104, ///< <a href="https://en.wikipedia.org/wiki/Log-normal_distribution">Log-normal distribution.</a>
    NVPL_RAND_CONTINUOUS_DIST_EXPONENTIAL   = 105, ///< <a href="https://en.wikipedia.org/wiki/Exponential_distribution">Exponential distribution.</a>
    NVPL_RAND_CONTINUOUS_DIST_GAMMA         = 106, ///< <a href="https://en.wikipedia.org/wiki/Gamma_distribution">Gamma distribution.</a> Only supported by pseudorandom generators.</a>
    NVPL_RAND_CONTINUOUS_DIST_BETA          = 107, ///< <a href="https://en.wikipedia.org/wiki/Beta_distribution">Beta distribution.</a> Only supported by pseudorandom generators.</a>

    // Multi-variate Continuous
    NVPL_RAND_CONTINUOUS_DIST_DIRICHLET     = 201, ///< <a href="https://en.wikipedia.org/wiki/Dirichlet_distribution">Dirichlet distribution.</a> Only supported by pseudorandom generators.

    // Uni-variate Discrete
    NVPL_RAND_DISCRETE_DIST_POISSON     = 301,   ///< <a href="https://en.wikipedia.org/wiki/Poisson_distribution">Poisson distribution.</a>
/* \cond PRIVATE */
    NVPL_RAND_DISCRETE_DIST_UNIFORM     = 302,
/* \endcond */
    NVPL_RAND_DISCRETE_DIST_BERNOULLI   = 303,  ///< <a href="https://en.wikipedia.org/wiki/Bernoulli_distribution">Bernoulli distribution.</a>
    NVPL_RAND_DISCRETE_DIST_CATEGORICAL = 304,  ///< <a href="https://en.wikipedia.org/wiki/Categorical_distribution">Categorical distribution.</a>
    NVPL_RAND_DISCRETE_DIST_BINOMIAL    = 305,  ///< <a href="https://en.wikipedia.org/wiki/Binomial_distribution">Binomial distribution.</a> Only supported by pseudorandom generators.

    // Multi-variate Discrete
    NVPL_RAND_DISCRETE_DIST_MULTINOMIAL = 401, ///< <a href="https://en.wikipedia.org/wiki/Multinomial_distribution">Multinomial distribution.</a> Only supported by pseudorandom generators.

} nvplRandDistributionType_t;

/**
 * \brief Configuration to describe the properties of a data distribution.
*/
typedef struct nvplRandDistributionConfig // NOLINT: allow typedef in C header
{
    nvplRandDistributionType_t dist; ///< Distribution type
    /**
     * \brief For each of the distribution type, the double value \p a is:
     *
    * - NVPL_RAND_CONTINUOUS_DIST_UNIFORM: not used \n
    * - NVPL_RAND_CONTINUOUS_DIST_UNIFORM_RANGE : start value of the range (start, end] \n
    * - NVPL_RAND_CONTINUOUS_DIST_NORMAL : mean of the normal distribution \n
    * - NVPL_RAND_CONTINUOUS_DIST_LOGNORMAL : mean of the associated normal distribution \n
    * - NVPL_RAND_CONTINUOUS_DIST_EXPONENTIAL : location parameter of exponential distribution, \f$ \lambda \f$ \n
    * - NVPL_RAND_CONTINUOUS_DIST_GAMMA : shape parameter, \f$ \alpha > 0 \f$ \n
    * - NVPL_RAND_CONTINUOUS_DIST_BETA : shape parameter, \f$ \alpha > 0 \f$ \n
    * - NVPL_RAND_CONTINUOUS_DIST_DIRICHLET: not used \n
    * - NVPL_RAND_DISCRETE_DIST_POISSON : rate parameter, \f$ \lambda > 0 \f$ \n
    * - NVPL_RAND_DISCRETE_DIST_BERNOULLI : rate parameter, \f$ 1 >= \lambda >= 0 \f$ \n
    * - NVPL_RAND_DISCRETE_DIST_CATEGORICAL : not used \n
    * - NVPL_RAND_DISCRETE_DIST_BINOMIAL : rate parameter, \f$ 1 >= \lambda >= 0 \f$ \n
    */
    double a;

    /**
     * \brief For each of the distribution type, the double value \p b needs to be defined only for the following distributions:
     *
    * - NVPL_RAND_CONTINUOUS_DIST_UNIFORM_RANGE : end value of the range (start, end] \n
    * - NVPL_RAND_CONTINUOUS_DIST_NORMAL : stddev of normal distribution \n
    * - NVPL_RAND_CONTINUOUS_DIST_LOGNORMAL : stddev of associated normal distribution \n
    * - NVPL_RAND_CONTINUOUS_DIST_GAMMA : scale parameter, \f$ \beta > 0 \f$ \n
    * - NVPL_RAND_CONTINUOUS_DIST_BETA : shape parameter, \f$ \beta > 0 \f$ \n
    */
    double b;

    /**
     * \brief The double array \p p_array needs to be defined only for the following distributions:
     *
    * - NVPL_RAND_CONTINUOUS_DIST_DIRICHLET: shape parameter arrays of size k, all > 0 \n
    * - NVPL_RAND_DISCRETE_DIST_CATEGORICAL: probability arrays, all >= 0
    */
    double* p_array;

    /**
     * \brief The unsigned integer value \p nk needs to be defined only for the following distributions:
     *
    * - NVPL_RAND_CONTINUOUS_DIST_DIRICHLET: size of the shape parameters \n
    * - NVPL_RAND_DISCRETE_DIST_CATEGORICAL: size of the probability parameters, >1 (if =1, use Bernoulli) \n
    * - NVPL_RAND_DISCRETE_DIST_BINOMIAL : size of Bernoulli trials, >1 (if =1, use Bernoulli) \n
    * - NVPL_RAND_DISCRETE_DIST_MULTINOMIAL : size of the probability parameters, >1 \n
    */
    unsigned int nk;

    /**
     * \brief The unsigned integer value \p nt needs to be defined only for the following distribution:
     *
    * - NVPL_RAND_DISCRETE_DIST_MULTINOMIAL : size of the Bernoulli trials >1
    */
    unsigned int nt;

} nvplRandDistributionConfig_t;

/**
 * \brief NVPL RAND API return status.
*/
typedef enum nvplRandStatus // NOLINT : allow typedef in C header
{
    NVPL_RAND_STATUS_SUCCESS                    = 0,
    NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED  = 101, ///< Generator not initialized
    NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR       = 102, ///< Generator is wrong type
    NVPL_RAND_STATUS_DATA_NULLPTR               = 103, ///< Data ptr is nullptr
    NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE        = 104, ///< Length requested is not a multiple of dimension, or not a multiple of two
    NVPL_RAND_STATUS_PCG_INCREMENT_NOT_ODD      = 105, ///< Increment requested for PCG is not odd
    NVPL_RAND_STATUS_OUT_OF_RANGE               = 106, ///< Argument out of range
    NVPL_RAND_STATUS_DISTRIBUTION_CONFIGS_ERROR = 107, ///< Distribution parameters are not acceptable
    NVPL_RAND_STATUS_DISTRIBUTION_TYPE_ERROR    = 108, ///< Distribution type is not supported by the generator
    NVPL_RAND_STATUS_INTERNAL_ERROR             = 999  ///< Internal library error
    //NVPL_RAND_STATUS_VERSION_MISMATCH      = 100, ///< Header file and linked library version do not match
} nvplRandStatus_t;

/**
 * \brief Ordering types of results in memory for multi-threaded generators.
*/
typedef enum nvplRandOrdering // NOLINT: allow typedef in C header
{
    NVPL_RAND_ORDERING_PSEUDO_DEFAULT = 100, ///< Default ordering for pseudorandom results
    NVPL_RAND_ORDERING_PSEUDO_FAST    = 101, ///< Non-strict ordering with good performance but cannot recover offset
    NVPL_RAND_ORDERING_STRICT         = 102, ///< Strict ordering generating same sequence as single-thread results
    NVPL_RAND_ORDERING_CURAND_LEGACY  = 103, ///< Legacy sequence for pseudorandom, guaranteed to be the same with cuRAND results
/* \cond PRIVATE */
    NVPL_RAND_ORDERING_PSEUDO_BLOCK   = 104,
/* \endcond */
    NVPL_RAND_ORDERING_QUASI_DEFAULT  = 201 ///< Specific n-dimensional ordering for quasirandom results
} nvplRandOrdering_t;

/* \cond PRIVATE */
typedef struct nvpl_rand_base_generator* nvplRandGenerator_t; // NOLINT: allow typedef in C header
/* \endcond */

/**
 * \brief Create new random number generator of type \p rng_type
 * and returns it in \p *gen.
 *
 * Legal values for \p rng_type are:
 * - NVPL_RAND_RNG_PSEUDO_DEFAULT
 * - NVPL_RAND_RNG_PSEUDO_XORWOW
 * - NVPL_RAND_RNG_PSEUDO_MRG32K3A
 * - NVPL_RAND_RNG_PSEUDO_MT19937
 * - NVPL_RAND_RNG_PSEUDO_PHILOX4_32_10
 * - NVPL_RAND_RNG_PSEUDO_PCG
 * - NVPL_RAND_RNG_QUASI_DEFAULT
 * - NVPL_RAND_RNG_QUASI_SOBOL32
 * - NVPL_RAND_RNG_QUASI_SCRAMBLED_SOBOL32
 * - NVPL_RAND_RNG_QUASI_SOBOL64
 * - NVPL_RAND_RNG_QUASI_SCRAMBLED_SOBOL64
 *
 * When \p rng_type is NVPL_RAND_RNG_PSEUDO_DEFAULT, the type chosen is NVPL_RAND_RNG_PSEUDO_XORWOW.
 * When \p rng_type is NVPL_RAND_RNG_QUASI_DEFAULT, the type chosen is NVPL_RAND_RNG_QUASI_SOBOL32.
 *
 * \param gen Pointer to generator
 * \param rng_type Type of generator to create
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was not initialized \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the value for \p rng_type is invalid \n
 * - NVPL_RAND_STATUS_SUCCESS if the generator was generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandCreateGenerator(nvplRandGenerator_t* gen,
                                                       nvplRandRngType_t    rng_type) NVPL_RAND_NOEXCEPT;
/**
 * \brief Destroy an existing generator and free all memory associated with its state.
 *
 * \param gen Generator to destroy
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created \n
 * - NVPL_RAND_STATUS_SUCCESS if generator was destroyed successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandDestroyGenerator(nvplRandGenerator_t gen) NVPL_RAND_NOEXCEPT;

/**
 * \brief Return the \p version number of the NVPL RAND library.
 *
 * \param version RAND library version
 *
 * \return
 * - NVPL_RAND_STATUS_SUCCESS if the version number was successfully returned \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandGetVersion(int* version) NVPL_RAND_NOEXCEPT;

/**
 * \brief Set the seed value of the pseudo-random number generator.
 *
 * All values of seed are valid.  Different seeds will produce different sequences.
 * Different seeds will often not be statistically correlated with each other,
 * but some pairs of seed values may generate sequences which are statistically correlated.
 *
 * The default values \p seed are:
 * - 0ULL, for NVPL_RAND_RNG_PSEUDO_XORWOW
 * - 12345ULL, for NVPL_RAND_RNG_PSEUDO_MRG32K3A
 * - 5489ULL, for NVPL_RAND_RNG_PSEUDO_MT19937
 * - 0xdeadbeefdeadbeefULL, for NVPL_RAND_RNG_PSEUDO_PHILOX4_32_10
 * - 0x853c49e6748fea9bULL, for NVPL_RAND_RNG_PSEUDO_PCG
 *
 * \param gen  Generator to modify
 * \param seed Seed value
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the generator is not a pseudorandom number generator \n
 * - NVPL_RAND_STATUS_SUCCESS if generator seed was set successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandSetPseudoRandomGeneratorSeed(nvplRandGenerator_t      gen,
                                                                    const unsigned long long seed) NVPL_RAND_NOEXCEPT;

/**
 * \brief Set the increment of the PCG pseudo number generator.
 *
 * The increment value for PCG must always be odd. The default value of \p inc is 0xda3e39cb94b95bdbULL.
 *
 * \param gen Generator to modify
 * \param inc Increment value of PCG, controlling which subsequence is selected
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the generator is not PCG \n
 * - NVPL_RAND_STATUS_PCG_INCREMENT_NOT_ODD if the increment value is an even number \n
 * - NVPL_RAND_STATUS_SUCCESS if generator increment value was set successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandSetPCGRandomGeneratorIncrement(nvplRandGenerator_t      gen,
                                                                      const unsigned long long inc) NVPL_RAND_NOEXCEPT;

/**
 * \brief Set the absolute offset of the pseudo or quasirandom number generator.
 *
 * All values of offset are valid.  The offset position is absolute, not
 * relative to the current position in the sequence.
 *
 * For quasirandom generators, the offset is the absolute position in the sequence generated per dimension.
 *
 * The default values \p offset for all generators are 0ULL.

 * \param gen Generator to modify
 * \param offset Absolute offset position
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_SUCCESS if generator offset was set successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandSetGeneratorOffset(nvplRandGenerator_t      gen,
                                                          const unsigned long long offset) NVPL_RAND_NOEXCEPT;
/**
 * \brief Set subsequence number for the pseudo number generator.
 *
 * Set subsequence, or stream, number for the pseudo number generator to allow explicitly skipping subsequence by users.
 * The ability to generate multiple subsequences of pseudorandom numbers allows developing parallel random number
 * generation using the single-threaded NVPL RAND library.
 *
 * The subsequence position is absolute, not relative to the current state's subsequence.
 *
 * Supported pseudo random generators: XORWOW, MRG32K3A, PHILOX4_32_10, and PCG.
 *
 * Except for MRG32K3a, which has the max subsequence number \f$2^{51}\f$, all values of subsequence are valid.
 *
 * The API is recommended to only be used with a single-threaded generator.
 *
 * \param gen Generator to modify
 * \param seq Subsequence number to be set
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the API is not supported for the generator \n
 * - NVPL_RAND_STATUS_OUT_OF_RANGE if the subsequence number is out of range
 * - NVPL_RAND_STATUS_SUCCESS if generator subsequence was set successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandSetGeneratorSubsequence(nvplRandGenerator_t      gen,
                                                               const unsigned long long seq) NVPL_RAND_NOEXCEPT;

/**
 * \brief Set the number of dimensions for the quasirandom number generator.
 *
 * When generating results in *num_dims* dimensions, the size *n* output will consist of *n / num_dims* results from the *1st* dimension,
 * followed by *n / num_dims* results from the *2nd* dimension,
 * and so on up to the last dimension. Only exact multiples of the dimension size may be generated.
 *
 * Legal values for \p num_dims are 1 to 20000; the default is 1.
 *
 * \param gen Generator to modify
 * \param num_dims Number of dimensions
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created \n
 * - NVPL_RAND_STATUS_OUT_OF_RANGE if num_dimensions is not valid \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the generator is not a quasirandom number generator \n
 * - NVPL_RAND_STATUS_SUCCESS if the dimension was set successfully \n
 */
NVPL_RAND_API nvplRandStatus_t
nvplRandSetQuasiRandomGeneratorDimensions(nvplRandGenerator_t gen, const unsigned int num_dims) NVPL_RAND_NOEXCEPT;
/**
 * \brief Generate 32-bit pseudo or quasirandom numbers with XORWOW, MRG32K3A, MT19937, PHILOX4_32_10, PCG, SOBOL32, and Scrambled SOBOL32 generators.
 *
 * Use \p gen to generate \p num 32-bit results into the memory at
 * \p outputPtr. The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are 32-bit values with every bit random.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store generated results
 * \param num Number of random 32-bit values to generate
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the generator type does not match the data type \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE if the number of output samples is
 *    not a multiple of the quasirandom dimension \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandGenerate(nvplRandGenerator_t gen,
                                                unsigned int*       outputPtr,
                                                const size_t        num) NVPL_RAND_NOEXCEPT;

/**
 * \brief Generate 64-bit pseudo or quasirandom numbers with PCG, SOBOL64, and Scrambled SOBOL64 generators.
 *
 * Use \p gen to generate \p num 64-bit results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are 64-bit values with every bit random.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store generated results
 * \param num Number of random 64-bit values to generate
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the generator type is not a 64-bit generator \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE if the number of output samples is
 *    not a multiple of the quasirandom dimension \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateLongLong(nvplRandGenerator_t gen,
                                                        unsigned long long* outputPtr,
                                                        const size_t        num) NVPL_RAND_NOEXCEPT;

/**
 * \brief Generate uniformly distributed floats.
 *
 * Use \p gen to generate \p num float results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are FP32 uniformly distributed random values between between 0 and 1, excluding 0 and including 1.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store generated results
 * \param num Number of floats to generate
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE if the number of output samples is
 *    not a multiple of the quasirandom dimension \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateUniform(nvplRandGenerator_t gen,
                                                       float*              outputPtr,
                                                       const size_t        num) NVPL_RAND_NOEXCEPT;


/**
 * \brief Generate uniformly distributed doubles.
 *
 * Use \p generator to generate \p num float results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are FP64 uniformly distributed random values between 0 and 1, excluding 0 and including 1.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store generated results
 * \param num Number of doubles to generate
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE if the number of output samples is
 *    not a multiple of the quasirandom dimension \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
*/
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateUniformDouble(nvplRandGenerator_t gen,
                                                             double*             outputPtr,
                                                             const size_t        num) NVPL_RAND_NOEXCEPT;

/**
 * \brief Generate uniformly distributed floats with custom range.
 *
 * Use \p gen to generate \p num float results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are FP32 uniformly distributed random values between \p start and \p end,
 * excluding \p start and including \p end.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store generated results
 * \param num Number of floats to generate
 * \param start Start of the interval
 * \param end End of the interval
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE if the number of output samples is
 *    not a multiple of the quasirandom dimension \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateUniformRange(nvplRandGenerator_t gen,
                                                            float*              outputPtr,
                                                            const size_t        num,
                                                            const float         start,
                                                            const float         end) NVPL_RAND_NOEXCEPT;

/**
 * \brief Generate uniformly distributed doubles with custom range.
 *
 * Use \p gen to generate \p num float results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are FP64 uniformly distributed random values between
 * \p start and \p end, excluding \p start and including \p end.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store generated results
 * \param num Number of doubles to generate
 * \param start Start of the interval
 * \param end End of the interval
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE if the number of output samples is
 *    not a multiple of the quasirandom dimension \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
*/
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateUniformRangeDouble(nvplRandGenerator_t gen,
                                                                  double*             outputPtr,
                                                                  const size_t        num,
                                                                  const double        start,
                                                                  const double        end) NVPL_RAND_NOEXCEPT;

/**
 * \brief Generate normally distributed floats.
 *
 * Use \p gen to generate \p num float results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are FP32 normally distributed random values with mean \p mean and standard
 * deviation \p stddev.
 *
 * Normally distributed results are generated from pseudorandom generators
 * with a Box-Muller transform.
 * Quasirandom generators use an inverse cumulative distribution
 * function (ICDF) to preserve dimensionality.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store generated results
 * \param num Number of floats to generate
 * \param mean Mean of normal distribution
 * \param stddev Standard deviation of normal distribution
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE if the number of output samples is
 *    not a multiple of the quasirandom dimension, or is not a multiple
 *    of two for pseudorandom generators \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
*/
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateNormal(nvplRandGenerator_t gen,
                                                      float*              outputPtr,
                                                      const size_t        num,
                                                      const float         mean,
                                                      const float         stddev) NVPL_RAND_NOEXCEPT;

/**
 * \brief Generate normally distributed doubles.
 *
 * Use \p gen to generate \p num float results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are FP64 normally distributed random values with mean \p mean and standard
 * deviation \p stddev.
 *
 * Normally distributed results are generated from pseudorandom generators (except Mersenne Twister MT19937)
 * with a Box-Muller transform, so require \p num be to be even.
 * Quasirandom generators and Mersenne Twister MT19937 use an inverse cumulative distribution
 * function (ICDF) to preserve dimensionality.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store generated results
 * \param num Number of doubles to generate
 * \param mean Mean of normal distribution
 * \param stddev Standard deviation of normal distribution
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_LENGTH_NOT_MULTIPLE if the number of output samples is
 *    not a multiple of the quasirandom dimension, or is not a multiple
 *    of two for pseudorandom generators \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
*/
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateNormalDouble(nvplRandGenerator_t gen,
                                                            double*             outputPtr,
                                                            const size_t        num,
                                                            const double        mean,
                                                            const double        stddev) NVPL_RAND_NOEXCEPT;

/**
 * \brief Generate floats based on specified continuous distribution.
 *
 * Use \p gen to generate \p num float results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are FP32 random values with user-specified distribution \p config.
 * 
 * Normally distributed results are generated from pseudorandom generators (except Mersenne Twister MT19937)
 * with a Box-Muller transform, so require \p num be to be even.
 * Quasirandom generators and Mersenne Twister MT19937 use an inverse cumulative distribution
 * function (ICDF) to preserve dimensionality.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store the results
 * \param config Configurations of the distribution
 * \param num Number of floats to generate. For multi-variate distributions, e.g., Dirichlet,
 *  ( num * \p config.nk ) number of floats are generated.
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_DISTRIBUTION_TYPE_ERROR if the distribution type is not supported \n
 * - NVPL_RAND_STATUS_DISTRIBUTION_CONFIGS_ERROR if the distribution config is incorrectly set, or does not support certain ordering. Note that Gamma, Beta, and Dirichlet distributions do not support NVPL_RAND_ORDERING_STRICT order \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateDistribution(nvplRandGenerator_t                gen,
                                                            float*                             outputPtr,
                                                            const nvplRandDistributionConfig_t config,
                                                            const size_t                       num) NVPL_RAND_NOEXCEPT;
/**
 * \brief Generate doubles based on specified continuous distribution.
 *
 * Use \p gen to generate \p num double results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are FP64 random values with user-specified distribution \p config.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store the results
 * \param config Configurations of the distribution
 * \param num Number of floats to generate. For multi-variate distributions, e.g., Dirichlet,
 *  ( num * \p config.nk ) number of doubles are generated.
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_DISTRIBUTION_TYPE_ERROR if the distribution type is not supported \n
 * - NVPL_RAND_STATUS_DISTRIBUTION_CONFIGS_ERROR if the distribution config is incorrectly set, or does not support certain ordering. Note that Gamma, Beta, and Dirichlet distributions do not support NVPL_RAND_ORDERING_STRICT order \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateDistributionDouble(nvplRandGenerator_t                gen,
                                                                  double*                            outputPtr,
                                                                  const nvplRandDistributionConfig_t config,
                                                                  const size_t num) NVPL_RAND_NOEXCEPT;

/**
 * \brief Generate unsigned integers based on specified discrete distribution.
 *
 * Use \p gen to generate \p num integer results into the memory at
 * \p outputPtr.  The memory must have been previously allocated and be
 * large enough to hold all the results.
 *
 * Results are 32-bit random integer values with user-specified distribution \p config.
 *
 * \param gen Generator to use
 * \param outputPtr Pointer to the memory to store the results
 * \param distConfig Configurations of the distribution
 * \param num Number of unsigned integers to generate. For multi-variate distributions, e.g., multinomial,
 *  ( num * \p config.nk ) number of unsigned integers are generated.
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was never created   \n
 * - NVPL_RAND_STATUS_DATA_NULLPTR if outputPtr is nullptr             \n
 * - NVPL_RAND_STATUS_DISTRIBUTION_TYPE_ERROR if the distribution type is not supported \n
 * - NVPL_RAND_STATUS_DISTRIBUTION_CONFIGS_ERROR if the distribution config is incorrectly set, or does not support certain ordering. Note that Poison distribution does not support NVPL_RAND_ORDERING_STRICT order \n
 * - NVPL_RAND_STATUS_SUCCESS if the results were generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandGenerateDistributionDiscrete(nvplRandGenerator_t                gen,
                                                                    unsigned int*                      outputPtr,
                                                                    const nvplRandDistributionConfig_t distConfig,
                                                                    const size_t num) NVPL_RAND_NOEXCEPT;

// nvplRandMT APIs
/**
 * \brief Create a new random number generator of type \p rng_type, set the number of threads to be
 * \p nthreads, and returns it in \p *gen.
 *
 * Legal values for \p rng_type are:
 * - NVPL_RAND_RNG_PSEUDO_DEFAULT
 * - NVPL_RAND_RNG_PSEUDO_XORWOW
 * - NVPL_RAND_RNG_PSEUDO_MRG32K3A
 * - NVPL_RAND_RNG_PSEUDO_PHILOX4_32_10
 * - NVPL_RAND_RNG_PSEUDO_PCG
 * - NVPL_RAND_RNG_QUASI_DEFAULT
 * - NVPL_RAND_RNG_QUASI_SOBOL32
 * - NVPL_RAND_RNG_QUASI_SCRAMBLED_SOBOL32
 * - NVPL_RAND_RNG_QUASI_SOBOL64
 * - NVPL_RAND_RNG_QUASI_SCRAMBLED_SOBOL64
 *
 * When \p rng_type is \p NVPL_RAND_RNG_PSEUDO_DEFAULT, the type chosen is \p NVPL_RAND_RNG_PSEUDO_XORWOW. When \p rng_type
 * is NVPL_RAND_RNG_QUASI_DEFAULT, the type chosen is \p NVPL_RAND_RNG_QUASI_SOBOL32.
 *
 * The API can only be used when linking to the multi-threaded NVPL RAND library.
 *
 * \param gen Pointer to generator
 * \param rng_type Type of generator to create
 * \param nthreads Number of threads used to generate random numbers
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was not initialized \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the value for \p rng_type is invalid \n
 * - NVPL_RAND_STATUS_SUCCESS if the generator was generated successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandMTCreateGenerator(nvplRandGenerator_t* gen,
                                                         nvplRandRngType_t    rng_type,
                                                         const unsigned int   nthreads) NVPL_RAND_NOEXCEPT;
/**
 * \brief Create a new random number generator of type \p rng_type, set the number of threads to be
 * the value of std::thread::hardware_concurrency(), and returns it in \p *gen.
 *
 * The API can only be used when linking to the multi-threaded NVPL RAND library.
 *
 * \param gen Pointer to generator
 * \param rng_type Type of generator to create
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was not initialized \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the value for \p rng_type is invalid \n
 * - NVPL_RAND_STATUS_SUCCESS if the generator was generated successfully \n
*/
NVPL_RAND_API nvplRandStatus_t nvplRandMTCreateGeneratorDefault(nvplRandGenerator_t* gen,
                                                                nvplRandRngType_t    rng_type) NVPL_RAND_NOEXCEPT;

/**
 * \brief Set the ordering of results of the pseudo or quasirandom number generator.
 *
 *
 * Legal values of \p order for pseudorandom generators are:
 * - NVPL_RAND_ORDERING_PSEUDO_DEFAULT
 * - NVPL_RAND_ORDERING_PSEUDO_FAST
 * - NVPL_RAND_ORDERING_STRICT
 * - NVPL_RAND_ORDERING_CURAND_LEGACY
 *
 * Legal values of \p order for quasirandom generators are:
 * - NVPL_RAND_ORDERING_QUASI_DEFAULT
 *
 * The API can only be used when linking to the multi-threaded NVPL RAND library.
 *
 * \param gen Generator to modify
 * \param order Ordering of results
 *
 * \return
 * - NVPL_RAND_STATUS_GENERATOR_NOT_INITIALIZED if the generator was not initialized \n
 * - NVPL_RAND_STATUS_GENERATOR_TYPE_ERROR if the generator does not support the ordering type \n
 * - NVPL_RAND_STATUS_SUCCESS if the generator ordering was set successfully \n
 */
NVPL_RAND_API nvplRandStatus_t nvplRandMTSetGeneratorOrdering(nvplRandGenerator_t gen,
                                                              nvplRandOrdering_t  order) NVPL_RAND_NOEXCEPT;

#ifdef __cplusplus
}
#endif

/** @} */

#endif // NVPL_RAND_H
