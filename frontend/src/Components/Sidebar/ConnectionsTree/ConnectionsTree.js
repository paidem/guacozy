import React, {useContext, useLayoutEffect, useState} from 'react';
import Tree from "rc-tree";
import './ConnectionsTree.css'
import {AppContext} from "../../../Context/AppContext";
import {LayoutContext} from "../../../Layout/LayoutContext";


function ConnectionsTree({searchString, draggable}) {
    const [appState,] = useContext(AppContext);
    const [layoutState,] = useContext(LayoutContext);
    const [treeData, setTreeData] = useState([]);

    useLayoutEffect(() => {
            /***
             * This function recursively converts our objects to nodes prepared for rc-tree
             * {title, key, children}
             * all other fields are for our user
             * @param node
             * @returns {{hidden: boolean, children: (*|[]), appid: *, filtertext: *, title: *, isLeaf: boolean, key: string}}
             */
            const convertTreeNode = (node) => {
                let newTreeNode = {
                    title: node.text,
                    key:  node.id,
                    isLeaf: !node.isFolder,
                    appid: node.id,
                    filtertext: node.text,
                    hidden: false,
                    children: node.isFolder ? node.children.map(child => convertTreeNode(child)) : []
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

            searchString && filterTree(newTreeData, searchString);

            setTreeData([...newTreeData]);

        },
        [appState.connections, searchString, appState.actions, layoutState.actions]
    );


    return (
        <React.Fragment>
            {treeData.length > 0 ?
                <Tree
                    defaultExpandAll
                    selectable={false}
                    filterTreeNode={(node) => node.props.hidden}
                    treeData={treeData}
                    draggable={draggable}
                />
                : null}
        </React.Fragment>
    );
}

export default ConnectionsTree;