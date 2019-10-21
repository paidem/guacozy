import {Icon} from "semantic-ui-react";
import React from "react";

const getIcon = (isFolder, protocol) => {
        if (isFolder) {
            return <Icon name='folder outline' size="small" color="yellow"/>;
        }

        switch (protocol) {
            case "rdp":
                return <Icon name='computer' size="small" color="blue"/>;
            case "ssh":
                return <Icon name='terminal' size="small" color="green"/>;
            case "vnc":
                return <Icon name='computer' size="small" color="green"/>;
            default:
                return <Icon name='computer' size="small"/>;
        }
    };

export default getIcon;