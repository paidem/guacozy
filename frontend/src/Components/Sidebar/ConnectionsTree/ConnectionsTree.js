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
    const [expandedKeys, setExpandedKeys] = useState([]);
    const [stashedExpandedKeys, setStashedExpandedKeys] = useState([]);


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
                , []), "key")
    }, []);

    // Determines which API calls should be made to update hierarchy to desired state
    // and makes API calls
    const saveHierarchyChanges = () => {
        setSaving(true);
        let flatInitialTree = flattenTreeParent(initialTreeData, 0);
        let flatTree = flattenTreeParent(treeData, 0,);

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


    const getConnectionsCount = useCallback(node => {
        return node.children ? node.children.filter(n => n.isFolder).reduce(function (total, child) {
            return total + getConnectionsCount(child)
        }, node.children.filter(n => !n.isFolder).length) : 0;
    }, []);

    const expandMode = {
        COLLAPSE_ALL: 1,
        EXPAND_SHALLOW: 2,
        EXPAND_ALL: 3,
    };

    /***
     *  Sets initial expandedKeys state, which is defined as
     *  "Expand all folders which contain folders"
     * @param tree
     * @param expandToNodes - if "leaf" folders (which have only connections in them) should be expanded
     */
    const expandTree = useCallback((tree, exMode = 2) => {
        let newExpandedKeys = [];

        switch (exMode) {
            case expandMode.COLLAPSE_ALL:
                newExpandedKeys = [-1];
                break;
            case expandMode.EXPAND_ALL:
                flattenTreeParent(tree)
                    .forEach(n => {
                        if (!n.hidden && !n.isLeaf) {
                            newExpandedKeys.push(n.key);
                        }
                    });
                break;
            case expandMode.EXPAND_SHALLOW:
                flattenTreeParent(tree)
                    .forEach(n => {
                        if (!n.hidden && !n.isLeaf && n.children.filter(node => !node.isLeaf).length > 0) {
                            newExpandedKeys.push(n.key);
                        }
                    });
                break;
            default:
                console.log("Unsupported treeExpandMode!");
                return;
        }

        if (JSON.stringify(expandedKeys.sort()) !== JSON.stringify(newExpandedKeys.sort())) {
            setExpandedKeys(newExpandedKeys);
            localStorage.setItem('expandedKeys', JSON.stringify(newExpandedKeys))
        }

    }, [expandMode.COLLAPSE_ALL, expandMode.EXPAND_ALL, expandMode.EXPAND_SHALLOW, expandedKeys, flattenTreeParent]);

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
                        className="nodeTitle"
                        onContextMenu={(e) => {
                            handleFolderContextMenuEvent(e, {
                                id: node.id.toString(),
                                name: node.text
                            })
                        }}
                    >
                        {getIcon(true, null)}
                        {node.text}
                        &nbsp;<span className="connectionCount"> {getConnectionsCount(node)}</span>
                    </span>
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
            const convertTreeNode = (node) => ({
                title: nodeTitleConstructor(node),
                key: node.id.toString(),
                isLeaf: !node.isFolder,
                appid: node.id,
                filtertext: node.text,
                hidden: false,
                subFolderCount: node.isFolder ? node.children.filter(n => n.isFolder).length : 0,
                children: node.isFolder ? sortArrayOfObjects(node.children.map(child => convertTreeNode(child)), 'filtertext') : []
            });


            /***
             * set item's visibility according to filter term
             * also resolve parents visibility so if an object (connection) is visible
             * all it's ancestors are visible
             */
            const filterTree = (items, term) => {
                return items.map(item => {
                    // by default item is hidden
                    item.hidden = true;

                    // unhide if item has search term in filtertext
                    if (item.filtertext.toLowerCase().includes(term.toLowerCase())) {
                        item.hidden = false;
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

            /***
             * Try to load expanded folders list from Local Storage. Return true on success
             */
            const loadExpandedKeyFromLocalStorage = () => {
                let loadedExpandedKeys = JSON.parse(localStorage.getItem("expandedKeys"));
                if (Array.isArray(loadedExpandedKeys) && loadedExpandedKeys.length > 0) {
                    setExpandedKeys(loadedExpandedKeys);
                }
            };


            // Effect actions start

            /// convert connection tree from application state to rc-tree format
            let newTreeData = appState.connections.map(node => convertTreeNode(node));

            // Save initial tree data so we can later compared if dragging changed it's hierarchy
            setInitialTreeData(JSON.parse(JSON.stringify(newTreeData)));

            // Check if we are in a search mode
            if (searchString) {
                // Filter tree to searchString
                newTreeData = filterTree(newTreeData, searchString);

                // Save expandedKeys state before changing expandedKeys
                if (stashedExpandedKeys.length === 0) {
                    setStashedExpandedKeys(expandedKeys);
                }

                expandTree(newTreeData, expandMode.EXPAND_ALL);

                setTreeData([...newTreeData]);
                return;
            }

            // Check if we have stashed expanded keys. They are saved before entering filter mode
            // if they are saved - we have just exited filter mode and have to restore state.
            if (stashedExpandedKeys.length > 0) {
                setExpandedKeys(stashedExpandedKeys);
                setStashedExpandedKeys([]);
            }

            // Check if page was just loaded - first time load (when expanded keys are blank)
            if (expandedKeys.length === 0) {
                loadExpandedKeyFromLocalStorage();
                expandTree(newTreeData, expandMode.EXPAND_SHALLOW);
            }

            setTreeData([...newTreeData]);

        },
        [appState.connections, searchString, appState.actions, layoutState.actions, appState.user, flattenTreeParent, getConnectionsCount, stashedExpandedKeys, expandedKeys, expandTree, expandMode.EXPAND_ALL, expandMode.EXPAND_SHALLOW]
    );

    const onExpand = (keys) => {
        setExpandedKeys(keys);
        localStorage.setItem('expandedKeys', JSON.stringify(keys))
    };

    const getContent = () => {
        if (treeData.length === 0) {
            if (appState.connectionsLoading) {
                return "Loading"
            }
            return <p>Empty</p>
        }

        return <Tree
            expandedKeys={expandedKeys}
            onExpand={onExpand}
            selectable={false}
            filterTreeNode={(node) => node.props.hidden}
            treeData={treeData}
            draggable={draggable}
            onDrop={onDrop}
        />
    };

    return (
        <React.Fragment>
            <Button icon='arrow up'
                    color='grey'
                    basic
                    inverted
                    size='mini'
                    title='Collapse all'
                    className='topButtonLeft'
                    onClick={() => {
                        expandTree(treeData, expandMode.COLLAPSE_ALL);
                    }
                    }
            />
            <Button icon='folder outline'
                    color='grey'
                    basic
                    inverted
                    size='mini'
                    title='Shallow expand'
                    className='topButtonLeft'
                    onClick={() => {
                        expandTree(treeData, expandMode.EXPAND_SHALLOW);
                    }
                    }
            />
            <Button icon='list'
                    color='grey'
                    basic
                    inverted
                    size='mini'
                    title='Expand all'
                    className='topButtonLeft'
                    onClick={() => {
                        expandTree(treeData, expandMode.EXPAND_ALL);
                    }
                    }
            />
            {treeChanged ||
            <Button icon='save'
                    color='red'
                    inverted
                    size='mini'
                    title='Save'
                    className='topButtonRight'
                    loading={saving}
                    onClick={() => {
                        saveHierarchyChanges();
                    }
                    }
            />}
            <div id="connectionTree">
                {getContent()}
            </div>
        </React.Fragment>
    );
}

export default ConnectionsTree;