import React from 'react';
import Welcome from "../Components/Welcome/Welcome";
import ConnectionSidebar from "../Components/Sidebar/ConnectionSidebar/ConnectionSidebar";

export const layoutFactory = (node) => {
        var component = node.getComponent();
        if (component === 'welcomeScreen'){
            return <Welcome />
        }
        if (component === "ConnectionSidebar") {
            return <ConnectionSidebar/>
        }
        if (component === "SettingsSidebar") {
            return <div/>
        }
        if (component === "GuacViewer") {
            return <div />
        }        
        if (component === "TabIframe") {
            return <div />
        }
    };