import React, {useContext} from 'react';
import {LayoutContext} from "../../../Layout/LayoutContext";

function TabLink({url, tabName, linkName, visible = true}) {
    const [layoutState,] = useContext(LayoutContext);

    const onClickHandler = (e) => {
        // prevent opening link
        e.preventDefault();

        // instead create nre IframeTab
        layoutState.actions.addIframeTab({
            url: url,
            name: tabName
        })
    };

    return (
        visible &&
        <a href={url} onClick={onClickHandler}
           style={{cursor: "pointer"}}>
            {linkName}
        </a>
    );
}

export default TabLink;