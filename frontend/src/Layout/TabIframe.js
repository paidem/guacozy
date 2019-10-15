import React from 'react';

function TabIframe({url, name}) {
    return (
        <iframe style={{width:"100%", height:"100%", backgroundColor:"white"}} src={url} title={name}>
        </iframe>
    );
}

export default TabIframe;