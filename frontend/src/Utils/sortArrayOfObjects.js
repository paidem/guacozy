export function sortArrayOfObjects(arr, sortKey) {
    return arr.sort((a, b) => a[sortKey] > b[sortKey] ? 1 : (a[sortKey] === b[sortKey] ? 0 : -1));
}