import React, {useCallback, useContext, useEffect, useLayoutEffect, useState} from 'react';
import Tree from "rc-tree";
import './ConnectionsTree.css'
import {AppContext} from "../../../Context/AppContext";
import {LayoutContext} from "../../../Layout/LayoutContext";
import {Button} from "semantic-ui-react";
import {handleConnectionContextMenuEvent} from "../../ContextMenu/ConnectionContextMenu";
import {handleFolderContextMenuEvent} from "../../ContextMenu/FolderContextMenu";
import getIcon from "../../../Utils/getIcon";
import {sortArrayOfObjects} from "../../../Utils/sortArrayOfObjects";

function ConnectionsTree({searchString, draggable, disableDraggebleMode}) {
    const [appState,] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);
    const [treeData, setTreeData] = useState([]);
    const [initialTreeData, setInitialTreeData] = useState([]);
    const [treeChanged, setTreeChanged] = useState(false);
    const [saving, setSaving] = useState(false);

    // Taken from author's example:
    // http://react-component.github.io/tree/examples/draggable.html
    const onDrop = useCallback(
        (info) => {
            const dropKey = info.node.props.eventKey;
            const dragKey = info.dragNode.props.eventKey;
            const dropPos = info.node.props.pos.split('-');
            const dropPosition = info.dropPosition - Number(dropPos[dropPos.length - 1]);

            // Will not drop connection directly on connection
            if (info.node.props.isLeaf && dropPosition === 0) {
                return;
            }

            const loop = (data, key, callback) => {
                data.forEach((item, index, arr) => {
                    if (item.key === key) {
                        callback(item, index, arr);
                        return;
                    }
                    if (item.children) {
                        loop(item.children, key, callback);
                    }
                });
            };

            const data = [...treeData];

            // Find dragObject and delete it from tree
            let dragObj;
            loop(data, dragKey, (item, index, arr) => {
                arr.splice(index, 1);
                dragObj = item;
            });

            if (!info.dropToGap) {
                // Drop on the content
                loop(data, dropKey, (item) => {
                    item.children = item.children || [];
                    // where to insert
                    item.children.push(dragObj);
                });
            } else if (
                (info.node.props.children || []).length > 0 &&  // Has children
                info.node.props.expanded &&                     // Is expanded
                dropPosition === 1                              // On the bottom gap
            ) {
                loop(data, dropKey, (item) => {
                    item.children = item.children || [];
                    // where to insert
                    item.children.unshift(dragObj);
                });
            } else {
                // Drop on the gap
                let ar;
                let i;
                loop(data, dropKey, (item, index, arr) => {
                    ar = arr;
                    i = index;
                });
                if (dropPosition === -1) {
                    ar.splice(i, 0, dragObj);
                } else {
                    ar.splice(i + 1, 0, dragObj);
                }
            }

            setTreeData(data)
        }, [treeData]);

    // Convert tree to flat objects and add "parent" reference
    const flattenTreeParent = useCallback((tree, parent = 0) => {
        return sortArrayOfObjects(tree
            .reduce((acc, node) =>
                    (acc.concat([{...node, parent: parent}])
                        .concat(node.children.length > 0
                            ?
                            flattenTreeParent(node.children, node.appid)
                            : []))
                , []),"key")
    }, []);

    // Determines which API calls should be made to update hierarchy to desired state
    // and makes API calls
    const saveHierarchyChanges = () => {
        setSaving(true);
        let flatInitialTree = flattenTreeParent(initialTreeData, 0);
        let flatTree = flattenTreeParent(treeData, 0, );

        let updates = [];

        for (let i = 0; i < flatInitialTree.length; i++) {
            if (flatTree[i].parent !== flatInitialTree[i].parent) {
                updates.push({
                    id: flatTree[i].appid,
                    parentid: flatTree[i].parent,
                    isFolder: !flatTree[i].isLeaf,
                });

            }
        }

        Promise.all(updates.map(update => appState.api.updateNodeLocation(update)))
            .finally(() => {
                appState.actions.updateConnections();
                setSaving(false);
                disableDraggebleMode()
            });
    };

    // This effect determines if tree hierarchy has been changed
    useEffect(() => {

        // Check if two trees are hierarchy is equal
        const hierarchyUnchanged = (A, B) => {
            let flatA = flattenTreeParent(A);
            let flatB = flattenTreeParent(B);

            if (flatA.length !== flatB.length) return false;

            for (let i = 0; i < flatA.length; i++) {
                if (flatA[i].parent !== flatB[i].parent) {
                    return false
                }
            }

            return true;
        };

        if (initialTreeData && treeData) {
            setTreeChanged(hierarchyUnchanged(initialTreeData, treeData, "key"));
        }
    }, [initialTreeData, treeData, flattenTreeParent]);


    // Effect which builds tree data from connections and search string
    useLayoutEffect(() => {
            /***
             * Takes node and returns it's representation. By default representation is just text
             * but here we use it mainly to bind to onDoubleClick event when clicking on connection node
             * @param node
             * @returns {*}
             */
            const nodeTitleConstructor = (node) => {
                if (node.isFolder) {
                    return <span
                        onContextMenu={(e) => {
                            handleFolderContextMenuEvent(e, {
                                id: node.id.toString(),
                                name: node.text
                            })
                        }}
                    > {getIcon(true, null)}{node.text}</span>
                } else {
                    return <span
                        onDoubleClick={() => appState.actions.activateConnection(node.id, node.text, appState.user)}
                        onContextMenu={(e) => {
                            handleConnectionContextMenuEvent(e, {
                                id: node.id.toString(),
                                text: node.text
                            })
                        }}
                    >{getIcon(false, node.protocol)}{node.text}</span>
                }
            };

            /***
             * This function recursively converts our objects to nodes prepared for rc-tree
             * {title, key, children}
             * all other fields are for our user
             * @param node
             * @returns {{hidden: boolean, children: (*|[]), appid: *, filtertext: *, title: *, isLeaf: boolean, key: string}}
             */
            const convertTreeNode = (node) => {
                let newTreeNode = {
                    title: nodeTitleConstructor(node),
                    key: node.id.toString(),
                    isLeaf: !node.isFolder,
                    appid: node.id,
                    filtertext: node.text,
                    hidden: false,
                    children: node.isFolder ? sortArrayOfObjects(node.children.map(child => convertTreeNode(child)),'filtertext') : []
                };

                return newTreeNode
            };

            // set item's visibility according to filter term
            // also resolve parents visibility so if an object (connection) is visible
            // all it's ancestors are visible
            const filterTree = (items, term) => {
                return items.map(item => {
                    // by default item is hidden
                    item.hidden = true;

                    // unhide if item has search term in filtertext
                    if (item.filtertext.toLowerCase().includes(term.toLowerCase())) {
                        item.hidden = false
                    }

                    // unhide if any of children is not hidden
                    if (item.children && item.children.length > 0) {
                        let childitems = filterTree(item.children, term);
                        if (childitems && childitems.length > 0) {
                            // acc wil become true if any of children hidden == false
                            let oneOfChildrenIsVisible = childitems.reduce((acc, newItem) => {
                                return acc || !newItem.hidden
                            }, false);

                            if (oneOfChildrenIsVisible) {
                                item.hidden = false;
                            }
                        }
                    }

                    return item
                });
            };


            let newTreeData = appState.connections.map(node => convertTreeNode(node));

            // Set initial tree data so we can later compared if dragging changed it's hierarchy
            setInitialTreeData(JSON.parse(JSON.stringify(newTreeData)));

            searchString && filterTree(newTreeData, searchString);

            setTreeData([...newTreeData]);

        },
        [appState.connections, searchString, appState.actions, layoutState.actions, appState.user]
    );

    const getContent = () => {
        if (treeData.length === 0) {
            if (appState.connectionsLoading) {
                return "Loading"
            }
            return <p>Empty</p>
        }

        return <Tree
            defaultExpandAll
            selectable={false}
            filterTreeNode={(node) => node.props.hidden}
            treeData={treeData}
            draggable={draggable}
            onDrop={onDrop}
        />
    };

    return (
        <React.Fragment>
            {treeChanged ||
            <Button icon='save'
                    color='red'
                    inverted
                    size='mini'
                    title='Save'
                    className='topButton'
                    loading={saving}
                    onClick={() => {
                        saveHierarchyChanges();
                    }
                    }
            />}
            {getContent()}
        </React.Fragment>
    );
}

export default ConnectionsTree;