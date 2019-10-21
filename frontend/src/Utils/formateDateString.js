export const formatDateString = (source, withSeconds = false) => {
    let date = new Date(source);
    let result = date.getFullYear() + "-" +
        (date.getMonth() + 1).toString().padStart(2, '0') +
        "-" +
        date.getDate().toString().padStart(2, '0') +
        " " +
        date.getHours().toString().padStart(2, '0') + ":" +
        date.getMinutes().toString().padStart(2, '0');

    if (withSeconds) {
        result += ":" + date.getSeconds().toString().padStart(2, '0')
    }

    return result;
};
