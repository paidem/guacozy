import React from 'react';
import Welcome from "../Components/Welcome/Welcome";
import ConnectionSidebar from "../Components/Sidebar/ConnectionSidebar/ConnectionSidebar";
import GuacViewer from "../Components/GuacViewer/GuacViewer";
import TabIframe from "./TabIframe";
import SettingsSidebar from "../Components/Sidebar/SettingsSidebar/SettingsSidebar";

export const layoutFactory = (node) => {
        var component = node.getComponent();
        if (component === 'welcomeScreen'){
            return <Welcome />
        }
        if (component === "ConnectionSidebar") {
            return <ConnectionSidebar/>
        }
        if (component === "SettingsSidebar") {
            return <SettingsSidebar/>
        }
        if (component === "GuacViewer") {
            return <GuacViewer {...node.getConfig()} node={node}/>
        }        
        if (component === "TabIframe") {
            return <TabIframe {...node.getConfig()} name={node.name}/>
        }
    };