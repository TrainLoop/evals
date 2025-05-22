/**
 * Utility functions for JSON handling
 */

/**
 * Type that converts BigInt to number recursively in complex types
 */
type ConvertBigIntToNumber<T> = T extends bigint
  ? number
  : T extends Array<infer U>
  ? Array<ConvertBigIntToNumber<U>>
  : T extends Object
  ? { [K in keyof T]: ConvertBigIntToNumber<T[K]> }
  : T;

/**
 * Recursively converts any BigInt values to regular numbers for JSON serialization
 * while maintaining the original object structure and type information
 * 
 * @param obj - The object containing potential BigInt values
 * @returns A new object with the same structure but BigInt values converted to numbers
 */
export function convertBigIntsToNumbers<T>(obj: T): ConvertBigIntToNumber<T> {
  if (obj === null || obj === undefined) {
    return obj as ConvertBigIntToNumber<T>;
  }

  // Handle BigInt values
  if (typeof obj === 'bigint') {
    return Number(obj) as ConvertBigIntToNumber<T>;
  }

  // Handle arrays
  if (Array.isArray(obj)) {
    return obj.map(convertBigIntsToNumbers) as ConvertBigIntToNumber<T>;
  }

  // Handle objects
  if (typeof obj === 'object') {
    const result = {} as Record<string, unknown>;
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        result[key] = convertBigIntsToNumbers((obj as Record<string, unknown>)[key]);
      }
    }
    return result as ConvertBigIntToNumber<T>;
  }

  // Return other primitives as is
  return obj as ConvertBigIntToNumber<T>;
}
