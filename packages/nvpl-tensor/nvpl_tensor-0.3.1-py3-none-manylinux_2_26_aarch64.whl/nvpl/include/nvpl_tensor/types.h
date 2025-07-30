/*
 * Copyright (c) 2019-23, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
 *
 * NVIDIA CORPORATION and its licensors retain all intellectual property
 * and proprietary rights in and to this software, related documentation
 * and any modifications thereto.  Any use, reproduction, disclosure or
 * distribution of this software and related documentation without an express
 * license agreement from NVIDIA CORPORATION is strictly prohibited.
 */


 /**
 * @file
 * @brief This file defines the types provided by the nvplTENSOR library.
 */
#pragma once

#include <stdint.h>


/**
 * \brief This enum specifies the data precision. It is used when the data reference does not carry the type itself (e.g void *)
 */
typedef enum
{
    NVPLTENSOR_R_32F  =  0, ///< real as a float
    NVPLTENSOR_C_32F  =  4, ///< complex as a pair of float numbers
    NVPLTENSOR_R_64F  =  1, ///< real as a double
    NVPLTENSOR_C_64F  =  5, ///< complex as a pair of double numbers
} nvpltensorDataType_t;

/**
 * \brief This enum captures all unary and binary element-wise operations supported by the nvplTENSOR library.
 */
typedef enum 
{
    /* Unary */
    NVPLTENSOR_OP_IDENTITY = 1,  ///< Identity operator (i.e., elements are not changed)
    NVPLTENSOR_OP_SQRT = 2,      ///< Square root
    NVPLTENSOR_OP_RELU = 8,      ///< Rectified linear unit
    NVPLTENSOR_OP_CONJ = 9,      ///< Complex conjugate
    NVPLTENSOR_OP_RCP = 10,      ///< Reciprocal
    NVPLTENSOR_OP_SIGMOID = 11,  ///< y=1/(1+exp(-x))
    NVPLTENSOR_OP_TANH = 12,     ///< y=tanh(x)
    NVPLTENSOR_OP_EXP = 22,      ///< Exponentiation.
    NVPLTENSOR_OP_LOG = 23,      ///< Log (base e).
    NVPLTENSOR_OP_ABS = 24,      ///< Absolute value.
    NVPLTENSOR_OP_NEG = 25,      ///< Negation.
    NVPLTENSOR_OP_SIN = 26,      ///< Sine.
    NVPLTENSOR_OP_COS = 27,      ///< Cosine.
    NVPLTENSOR_OP_TAN = 28,      ///< Tangent.
    NVPLTENSOR_OP_SINH = 29,     ///< Hyperbolic sine.
    NVPLTENSOR_OP_COSH = 30,     ///< Hyperbolic cosine.
    NVPLTENSOR_OP_ASIN = 31,     ///< Inverse sine.
    NVPLTENSOR_OP_ACOS = 32,     ///< Inverse cosine.
    NVPLTENSOR_OP_ATAN = 33,     ///< Inverse tangent.
    NVPLTENSOR_OP_ASINH = 34,    ///< Inverse hyperbolic sine.
    NVPLTENSOR_OP_ACOSH = 35,    ///< Inverse hyperbolic cosine.
    NVPLTENSOR_OP_ATANH = 36,    ///< Inverse hyperbolic tangent.
    NVPLTENSOR_OP_CEIL = 37,     ///< Ceiling.
    NVPLTENSOR_OP_FLOOR = 38,    ///< Floor.
    NVPLTENSOR_OP_MISH = 39,     ///< Mish y=x*tanh(softplus(x)).
    NVPLTENSOR_OP_SWISH = 40,    ///< Swish y=x*sigmoid(x).
    NVPLTENSOR_OP_SOFT_PLUS = 41, ///< Softplus y=log(exp(x)+1).
    NVPLTENSOR_OP_SOFT_SIGN = 42, ///< Softsign y=x/(abs(x)+1).
    /* Binary */
    NVPLTENSOR_OP_ADD = 3,       ///< Addition of two elements
    NVPLTENSOR_OP_MUL = 5,       ///< Multiplication of two elements
    NVPLTENSOR_OP_MAX = 6,       ///< Maximum of two elements
    NVPLTENSOR_OP_MIN = 7,       ///< Minimum of two elements

    NVPLTENSOR_OP_UNKNOWN = 126, ///< reserved for internal use only

} nvpltensorOperator_t;

/**
 * \brief nvplTENSOR status type returns
 *
 * \details The type is used for function status returns. All nvplTENSOR library functions return their status, which can have the following values.
 */
typedef enum 
{
    /** The operation completed successfully.*/
    NVPLTENSOR_STATUS_SUCCESS                = 0,
    /** The opaque data structure was not initialized.*/
    NVPLTENSOR_STATUS_NOT_INITIALIZED        = 1,
    /** Resource allocation failed inside the nvplTENSOR library.*/
    NVPLTENSOR_STATUS_ALLOC_FAILED           = 3,
    /** An unsupported value or parameter was passed to the function (indicates an user error).*/
    NVPLTENSOR_STATUS_INVALID_VALUE          = 7,
    /** An internal nvplTENSOR error has occurred.*/
    NVPLTENSOR_STATUS_INTERNAL_ERROR         = 14,
    /** The requested operation is not supported.*/
    NVPLTENSOR_STATUS_NOT_SUPPORTED          = 15,
    /** The functionality requested requires some license and an error was detected when trying to check the current licensing.*/
    NVPLTENSOR_STATUS_LICENSE_ERROR          = 16,
    /** The provided workspace was insufficient.*/
    NVPLTENSOR_STATUS_INSUFFICIENT_WORKSPACE = 19,
    /** Indicates an error related to file I/O.*/
    NVPLTENSOR_STATUS_IO_ERROR               = 21,
} nvpltensorStatus_t;

/**
 * \brief Allows users to specify the algorithm to be used for performing the desired
 * tensor operation.
 */
typedef enum
{
    NVPLTENSOR_ALGO_DEFAULT           = -1, ///< A performance model chooses the appropriate algorithm and kernel
} nvpltensorAlgo_t;

/**
 * \brief This enum gives users finer control over the suggested workspace
 *
 * \details This enum gives users finer control over the amount of workspace that is
 * suggested by \ref nvpltensorEstimateWorkspaceSize
 */
typedef enum
{
    NVPLTENSOR_WORKSPACE_MIN = 1,     ///< Least memory requirement; at least one algorithm will be available
    NVPLTENSOR_WORKSPACE_DEFAULT = 2, ///< Aims to attain high performance while also reducing the workspace requirement.
    NVPLTENSOR_WORKSPACE_MAX = 3,     ///< Highest memory requirement; all algorithms will be available (choose this option if memory footprint is not a concern)
} nvpltensorWorksizePreference_t;

/**
 * \brief Opaque structure representing a compute descriptor.
 */
typedef struct nvpltensorComputeDescriptor *nvpltensorComputeDescriptor_t;

#if defined(__cplusplus)
extern "C" {
#endif /* __cplusplus */
#ifndef NVPLTENSOR_EXTERN
#  ifdef _MSC_VER
#    define NVPLTENSOR_EXTERN __declspec(dllimport) extern
#  else
#    define NVPLTENSOR_EXTERN extern
#  endif
#endif
NVPLTENSOR_EXTERN const nvpltensorComputeDescriptor_t NVPLTENSOR_COMPUTE_DESC_32F;   ///< floating-point: 8-bit exponent and 23-bit mantissa (aka float)
NVPLTENSOR_EXTERN const nvpltensorComputeDescriptor_t NVPLTENSOR_COMPUTE_DESC_64F;   ///< floating-point: 11-bit exponent and 52-bit mantissa (aka double)
#if defined(__cplusplus)
}
#endif /* __cplusplus */


/**
 * This enum lists all attributes of a \ref nvpltensorOperationDescriptor_t that can be modified (see \ref nvpltensorOperationDescriptorSetAttribute and \ref nvpltensorOperationDescriptorGetAttribute).
 */
typedef enum
{
    NVPLTENSOR_OPERATION_DESCRIPTOR_TAG = 0,                  ///< int32_t: enables users to distinguish two identical problems w.r.t. the sw-managed plan-cache. (default value: 0)
    NVPLTENSOR_OPERATION_DESCRIPTOR_SCALAR_TYPE = 1,          ///< nvpltensorDataType_t: data type of the scaling factors
    NVPLTENSOR_OPERATION_DESCRIPTOR_FLOPS = 2,                ///< float: number of floating-point operations necessary to perform this operation (assuming all scalar are not equal to zero, unless otherwise specified)
    NVPLTENSOR_OPERATION_DESCRIPTOR_MOVED_BYTES = 3,          ///< float: minimal number of bytes transferred from/to global-memory  (assuming all scalar are not equal to zero, unless otherwise specified)
} nvpltensorOperationDescriptorAttribute_t;

/**
 * This enum lists all attributes of a \ref nvpltensorPlanPreference_t object that can be modified.
 */
typedef enum
{
    NVPLTENSOR_PLAN_PREFERENCE_ALGO = 3,             ///< nvpltensorAlgo_t: Fixes a certain \ref nvpltensorAlgo_t
} nvpltensorPlanPreferenceAttribute_t;

/**
 * This enum determines the mode w.r.t. nvplTENSOR's just-in-time compilation capability.
 */
typedef enum
{
    NVPLTENSOR_JIT_MODE_NONE = 0,    ///< Indicates that no kernel will be just-in-time compiled.
} nvpltensorJitMode_t;

/**
 * This enum lists all attributes of a \ref nvpltensorPlan_t object that can be retrieved via \ref nvpltensorPlanGetAttribute.
 *
 */
typedef enum
{
    NVPLTENSOR_PLAN_REQUIRED_WORKSPACE = 0, ///< uint64_t: exact required workspace in bytes that is needed to execute the plan
} nvpltensorPlanAttribute_t;

/**
 * \brief Opaque structure representing any type of problem descriptor (e.g., contraction, reduction, elementwise).
 */
typedef struct nvpltensorOperationDescriptor *nvpltensorOperationDescriptor_t;

/**
 * \brief Opaque structure representing a plan (e.g, contraction, reduction, elementwise).
 */
typedef struct nvpltensorPlan *nvpltensorPlan_t;

/**
 * \brief Opaque structure that narrows down the space of applicable
 * algorithms/variants/kernels.
 */
typedef struct nvpltensorPlanPreference *nvpltensorPlanPreference_t;

/**
 * \brief Opaque structure holding nvplTENSOR's library context.
 */
typedef struct nvpltensorHandle *nvpltensorHandle_t;

/**
 * \brief Opaque structure representing a tensor descriptor.
 */
typedef struct nvpltensorTensorDescriptor *nvpltensorTensorDescriptor_t;

/**
 * \brief A function pointer type for logging.
 */
typedef void (*nvpltensorLoggerCallback_t)(
        int32_t logLevel,
        const char* functionName,
        const char* message
);
