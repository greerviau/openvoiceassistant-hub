import React, { useState } from 'react';
import {
    FaBars,
    FaCogs,
    FaPlug,
    FaCode,
    FaRegChartBar,
    FaPowerOff
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
    
    const handlePowerOffClick = () => {
        // Display a confirmation popup
        const confirmRestart = window.confirm("Are you sure you want to restart?");
        
        if (confirmRestart) {
            // Call the /restart API or any other action on power off click
            fetch('/restart', {
                method: 'POST',
                // Add any required headers or credentials
            })
            .then(response => {
                // Handle the response if needed
            })
            .catch(error => {
                console.error('Error restarting:', error);
            });
        }
    };

    const menuItem=[
        {
            path:"/",
            name:"Overview",
            icon:<FaRegChartBar/>
        },
        {
            path:"/nodes",
            name:"Nodes",
            icon:<ImTree/>
        },
        {
            path:"/skills",
            name:"Skills",
            icon:<FaCogs/>
        },
        {
            path:"/integrations",
            name:"Integrations",
            icon:<FaPlug/>
        },
        {
            path:"/settings",
            name:"Settings",
            icon:<FiSettings/>
        },
        {
            path:"/logs",
            name:"Logs",
            icon:<FaCode/>
        }
    ]
    return (
        <div className="container">
           <div style={{width: isOpen ? "200px" : "50px"}} className="sidebar">
               <div className="top-section">
                   <h1 style={{display: isOpen ? "block" : "none"}} className="logo">v0.0.1</h1>
                   <div style={{marginLeft: isOpen ? "50px" : "0px"}} className="bars">
                       <FaBars onClick={toggle}/>
                   </div>
               </div>
               {
                   menuItem.map((item, index)=>(
                       <NavLink to={item.path} key={index} className="sidebar-item" activeclassname="active">
                           <div className="sidebar-icon">{item.icon}</div>
                           <div style={{display: isOpen ? "block" : "none"}} className="sidebar-text">{item.name}</div>
                       </NavLink>
                   ))
               }
                <div className="sidebar-power" activeclassname="active" onClick={handlePowerOffClick}>
                    <div className="sidebar-icon"><FaPowerOff /></div>
                    <div style={{display: isOpen ? "block" : "none"}} className="sidebar-text">Restart</div>
                </div>
           </div>
           <main>{children}</main>
        </div>
    );
};

export default Sidebar;