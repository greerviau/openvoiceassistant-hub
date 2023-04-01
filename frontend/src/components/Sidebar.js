import React, { useState } from 'react';
import {
    FaTh,
    FaBars,
    FaRegChartBar,
    FaTerminal
}from "react-icons/fa";
import {
    FiSettings
} from "react-icons/fi"
import {
    ImTree
} from "react-icons/im"
import { NavLink } from 'react-router-dom';


const Sidebar = ({children}) => {
    const[isOpen ,setIsOpen] = useState(false);
    const toggle = () => setIsOpen (!isOpen);
    const menuItem=[
        {
            path:"/",
            name:"Overview",
            icon:<FaTh/>
        },
        {
            path:"/nodes",
            name:"Nodes",
            icon:<ImTree/>
        },
        {
            path:"/skills",
            name:"Skills",
            icon:<FaRegChartBar/>
        },
        {
            path:"/settings",
            name:"Settings",
            icon:<FiSettings/>
        },
        {
            path:"/logs",
            name:"Logs",
            icon:<FaTerminal/>
        }
    ]
    return (
        <div className="container">
           <div style={{width: isOpen ? "200px" : "50px"}} className="sidebar">
               <div className="top_section">
                   <h1 style={{display: isOpen ? "block" : "none"}} className="logo">OVA v0.0.1</h1>
                   <div style={{marginLeft: isOpen ? "50px" : "0px"}} className="bars">
                       <FaBars onClick={toggle}/>
                   </div>
               </div>
               {
                   menuItem.map((item, index)=>(
                       <NavLink to={item.path} key={index} className="link" activeclassName="active">
                           <div className="icon">{item.icon}</div>
                           <div style={{display: isOpen ? "block" : "none"}} className="link_text">{item.name}</div>
                       </NavLink>
                   ))
               }
           </div>
           <main>{children}</main>
        </div>
    );
};

export default Sidebar;