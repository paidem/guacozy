import React, {useContext} from 'react';

import {contextMenu, Item, Menu, Separator} from "react-contexify";
import {AppContext} from "../../Context/AppContext";
import RenameFolderModal from "../Modals/RenameFolderModal";
import NewFolderModal from "../Modals/NewFolderModal";
import DeleteFolderModal from "../Modals/DeleteFolderModal";
import {LayoutContext} from "../../Layout/LayoutContext";

function FolderContextMenu(props) {
    const [appState,] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);

    const onFolderContextMenuAction = (event, props, action) => {
        switch (action) {
            case "new":
                appState.actions.openModal({type: NewFolderModal, data: {id: props.id, name: props.name}});
                break;
            case "rename":
                appState.actions.openModal({type: RenameFolderModal, data: {id: props.id, name: props.name}});
                break;
            case "delete":
                appState.actions.openModal({type: DeleteFolderModal, data: {id: props.id, name: props.name}});
                break;
             case "edit":
                layoutState.actions.addIframeTab({url: "/admin/backend/folder/" + props.id + "/change/", name : "*"+props.text});
                break;
            default:
                window.alert("Action not implemented: " + action);
        }
    };


    return (
        <Menu animation="fade" id="folder_context_menu" theme="dark">
            <Item
                onClick={({event, props}) => onFolderContextMenuAction(event, props, "new")}>New</Item>
            <Item
                onClick={({event, props}) => onFolderContextMenuAction(event, props, "rename")}>Rename</Item>
            {appState.user && appState.user.is_staff &&
            <Item
                onClick={({event, props}) => onFolderContextMenuAction(event, props, "edit")}>Edit</Item>
            }
            <Separator/>
            <Item
                onClick={({event, props}) => onFolderContextMenuAction(event, props, "delete")}>Delete</Item>
        </Menu>
    );
};

export default FolderContextMenu;

export const handleFolderContextMenuEvent = (e, data) => {
    e.preventDefault();
    contextMenu.show({
        id: "folder_context_menu",
        event: e,
        props: data
    });
};
