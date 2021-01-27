import xml.etree.ElementTree as ET

from .utils import DynamicsConstrains, TimeReference, convert_bool, TransitionDynamics, CatalogReference, Route, Trajectory, TrafficDefinition, Environment
from .utils import Controller
from .enumerations import DynamicsShapes, SpeedTargetValueType, FollowMode, ReferenceContext

from .position import _PositionType

class _ActionType():
    """ helper class for typesetting
    """
    pass
class _PrivateActionType(_ActionType):
    """ helper class for typesetting
    """
    pass
class _Action():
    """ Private class used to define an action, should not be used by the user.
        Used as a wrapper to create the extra elements needed
        
        Parameters
        ----------
            name (str): name of the action

            action (*Action): any action

        Attributes
        ----------
            name (str): name of the action

            action (*Action): any action

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    
    """

    def __init__(self,name,action):
        """ initalize _Action

        Parameters
        ----------
            name (str): name of the action

            action (*Action): any action

        """
        self.name = name
        
        self.action = action
        
    def get_attributes(self):
        """ returns the attributes of the _Action as a dict

        """
        return {'name':self.name}
        
    def get_element(self):
        """ returns the elementTree of the _Action

        """
        element = ET.Element('Action',attrib=self.get_attributes())
        element.append(self.action.get_element())
        return element


#### Private Actions ####

#LongitudinalAction

class AbsoluteSpeedAction(_PrivateActionType):
    """ The AbsoluteSpeedAction class specifies a LongitudinalAction of type SpeedAction with an abosulte target speed
        
        Parameters
        ----------
            speed (float): the speed wanted

            transition_dynamics (TransitionDynamics): how the change should be made

        Attributes
        ----------

            speed (float): the speed wanted

            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,speed,transition_dynamics):
        """ initalize the AbsoluteSpeedAction

        Parameters
        ----------
            speed (float): the speed wanted

            transition_dynamics (TransitionDynamics): how the change should be made

        """
        self.speed = speed
        if not isinstance(transition_dynamics,TransitionDynamics):
            raise TypeError('transition_dynamics input not of type TransitionDynamics')
        self.transition_dynamics = transition_dynamics
    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'value':str(self.speed)}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('PrivateAction')
        longaction = ET.SubElement(element,'LongitudinalAction')
        speedaction = ET.SubElement(longaction,'SpeedAction')

        speedaction.append(self.transition_dynamics.get_element('SpeedActionDynamics'))
        speedactiontarget = ET.SubElement(speedaction,'SpeedActionTarget')
        
        ET.SubElement(speedactiontarget,'AbsoluteTargetSpeed',self.get_attributes())
        
        return element

class RelativeSpeedAction(_PrivateActionType):
    """ The RelativeSpeedAction creates a LongitudinalAction of type SpeedAction with a relative target
        
        Parameters
        ----------
            speed (float): the speed wanted

            target (str): the name of the relative target (used for relative speed)

            transition_dynamics (TransitionDynamics): how the change should be made

            valuetype (str): the type of relative speed wanted (used for relative speed)

            continuous (bool): if the controller tries to keep the relative speed 

        Attributes
        ----------
            speed (float): the speed wanted

            target (str): the name of the relative target (used for relative speed)

            valuetype (str): the type of relative speed wanted (used for relative speed)

            continuous (bool): if the controller tries to keep the relative speed 

            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,speed,entity,transition_dynamics,valuetype='delta',continuous=True):
        """ initalizes RelativeSpeedAction

        Parameters
        ----------
            speed (float): the speed wanted

            target (str): the name of the relative target (used for relative speed)

            transition_dynamics (TransitionDynamics): how the change should be made

            valuetype (str): the type of relative speed wanted (used for relative speed)

            continuous (bool): if the controller tries to keep the relative speed 

        """
        self.speed = speed
        self.target = entity
        self.valuetype = valuetype
        if not isinstance(continuous,bool):
            raise TypeError('continuous input not of type bool')
        
        if not isinstance(transition_dynamics,TransitionDynamics):
            raise TypeError('transition_dynamics input not of type TransitionDynamics')
        self.transition_dynamics = transition_dynamics
        self.continuous = continuous

    
    def get_attributes(self):
        """ returns the attributes of the RelativeSpeedAction as a dict

        """
        return {'entityRef':self.target,'value':str(self.speed),'speedTargetValueType':self.valuetype,'continuous':convert_bool(self.continuous)}

    def get_element(self):
        """ returns the elementTree of the RelativeSpeedAction

        """
        element = ET.Element('PrivateAction')
        longaction = ET.SubElement(element,'LongitudinalAction')
        speedaction = ET.SubElement(longaction,'SpeedAction')
        speedaction.append(self.transition_dynamics.get_element('SpeedActionDynamics'))
        speedactiontarget = ET.SubElement(speedaction,'SpeedActionTarget')
        
        ET.SubElement(speedactiontarget,'RelativeTargetSpeed',self.get_attributes())
        
        return element
            
class LongitudinalDistanceAction(_PrivateActionType):
    """ The LongitudinalDistanceAction creates a LongitudinalAction of type LongitudinalDistanceAction with a distance target
        
        Parameters
        ----------
            distance (float): distance to the entity
            
            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continuous (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

        Attributes
        ----------
            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

            continuous (bool): if the controller tries to keep the relative speed 

            distance (float): the distance to the entity

            dynamic_constraint (DynamicsConstrains): Dynamics constraints of the action

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,distance,entity,freespace=True,continuous=True,max_acceleration = None,max_deceleration = None,max_speed = None):
        """ initalize the LongitudinalDistanceAction
        
        Parameters
        ----------
            distance (float): distance to the entity
            
            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continuous (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

        """
        self.target = entity
        if not isinstance(continuous,bool):
            raise TypeError('continuous input not of type bool')
        
        if not isinstance(freespace,bool):
            raise TypeError('freespace input not of type bool')


        self.freespace = freespace
        self.continuous = continuous
        self.dynamic_constraint = DynamicsConstrains(max_acceleration,max_deceleration,max_speed)
        self.distance = distance   
        

    def get_attributes(self):
        """ returns the attributes of the LongitudinalDistanceAction as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['freespace'] = convert_bool(self.freespace)
        retdict['continuous'] = convert_bool(self.continuous)
        retdict['distance'] = str(self.distance)
        return retdict

    def get_element(self):
        """ returns the elementTree of the LongitudinalDistanceAction

        """
        element = ET.Element('PrivateAction')
        longact = ET.SubElement(element,'LongitudinalAction')

        longdistaction = ET.SubElement(longact,'LongitudinalDistanceAction',attrib=self.get_attributes())
        if self.dynamic_constraint.is_filled():
            longdistaction.append(self.dynamic_constraint.get_element())
        return element

class LongitudinalTimegapAction(_PrivateActionType):
    """ The LongitudinalTimegapAction creates a LongitudinalAction of type LongitudinalDistanceAction with the timegap option
        
        Parameters
        ----------
            timegap (float): time to the target 

            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continuous (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

        Attributes
        ----------
            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

            continuous (bool): if the controller tries to keep the relative speed 

            timegap (float): timegap to the target

            dynamic_constraint (DynamicsConstrains): Dynamics constraints of the action

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,timegap,entity,freespace=True,continuous=True,max_acceleration = None,max_deceleration = None,max_speed = None):
        """ initalize the LongitudinalTimegapAction
        
        Parameters
        ----------
            timegap (float): time to the target 

            entity (str): the target name

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continuous (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None

        """
        self.target = entity
        if not isinstance(continuous,bool):
            raise TypeError('continuous input not of type bool')


        if not isinstance(freespace,bool):
            raise TypeError('freespace input not of type bool')


        self.freespace = freespace
        self.continuous = continuous
        self.timegap = timegap
        self.dynamic_constraint = DynamicsConstrains(max_acceleration,max_deceleration,max_speed)
        
       

    def get_attributes(self):
        """ returns the attributes of the LongitudinalTimegapAction as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['freespace'] = convert_bool(self.freespace)
        retdict['continuous'] = convert_bool(self.continuous)
        retdict['timeGap'] = str(self.timegap)
        return retdict

    def get_element(self):
        """ returns the elementTree of the LongitudinalTimegapAction

        """
        element = ET.Element('PrivateAction')
        longact = ET.SubElement(element,'LongitudinalAction')

        longdistaction = ET.SubElement(longact,'LongitudinalDistanceAction',attrib=self.get_attributes())
        if self.dynamic_constraint.is_filled():
            longdistaction.append(self.dynamic_constraint.get_element())
        return element

# lateral actions

class AbsoluteLaneChangeAction(_PrivateActionType):
    """ the AbsoluteLaneChangeAction creates a LateralAction of type LaneChangeAction with an absolute target
        
        Parameters
        ----------
            lane (int): lane to change to

            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        Attributes
        ----------
            lane (int): lane to change to

            target_lane_offset (float): offset in the target lane is wanted
                
            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,lane,transition_dynamics,target_lane_offset=None):
        """ initalize AbsoluteLaneChangeAction

        Parameters
        ----------
            lane (int): lane to change to

            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        """

        self.lane = lane
        self.target_lane_offset = target_lane_offset       
        if not isinstance(transition_dynamics,TransitionDynamics):
            raise TypeError('transition_dynamics input not of type TransitionDynamics')
        self.transition_dynamics = transition_dynamics

    def get_attributes(self):
        """ returns the attributes of the AbsoluteLaneChangeAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.lane)
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the AbsoluteLaneChangeAction

        """
        element = ET.Element('PrivateAction')
        laneoffset = {}
        lataction = ET.SubElement(element,'LateralAction')
        if self.target_lane_offset:
            laneoffset = {'targetLaneOffset':str(self.target_lane_offset)}
        lanechangeaction = ET.SubElement(lataction,'LaneChangeAction',attrib=laneoffset)

        
        lanechangeaction.append(self.transition_dynamics.get_element('LaneChangeActionDynamics'))
        lanchangetarget = ET.SubElement(lanechangeaction,'LaneChangeTarget')
        
        ET.SubElement(lanchangetarget,'AbsoluteTargetLane',self.get_attributes())
        return element


class RelativeLaneChangeAction(_PrivateActionType):
    """ the RelativeLaneChangeAction creates a LateralAction of type LaneChangeAction with a relative target
        
        Parameters
        ----------
            lane (int): relative lane number

            entity (str): the entity to run relative to
            
            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        Attributes
        ----------
            value (int): lane to change to

            target (str): target for relative lane change

            target_lane_offset (float): offset in the target lane is wanted
                
            transition_dynamics (TransitionDynamics): how the change should be made

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,lane,entity,transition_dynamics,target_lane_offset=None):
        """ initalize RelativeLaneChangeAction

        Parameters
        ----------
            lane (int): relative lane number

            entity (str): the entity to run relative to
            
            transition_dynamics (TransitionDynamics): how the change should be made

            target_lane_offset (float): if a offset in the target lane is wanted
                Default: None

        """

        self.lane = lane
        self.target = entity
        self.target_lane_offset = target_lane_offset
        if not isinstance(transition_dynamics,TransitionDynamics):
            raise TypeError('transition_dynamics input not of type TransitionDynamics')
        self.transition_dynamics = transition_dynamics


    def get_attributes(self):
        """ returns the attributes of the RelativeLaneChangeAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.lane)
        retdict['entityRef'] = self.target
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the RelativeLaneChangeAction

        """
        element = ET.Element('PrivateAction')
        laneoffset = {}
        lataction = ET.SubElement(element,'LateralAction')
        if self.target_lane_offset:
            laneoffset = {'targetLaneOffset':str(self.target_lane_offset)}
        lanechangeaction = ET.SubElement(lataction,'LaneChangeAction',attrib=laneoffset)
        
        lanechangeaction.append(self.transition_dynamics.get_element('LaneChangeActionDynamics'))
        lanchangetarget = ET.SubElement(lanechangeaction,'LaneChangeTarget')
        
        ET.SubElement(lanchangetarget,'RelativeTargetLane',self.get_attributes())
        return element

class AbsoluteLaneOffsetAction(_PrivateActionType):
    """ the AbsoluteLaneOffsetAction class creates a LateralAction of type LaneOffsetAction with an absolute target
        
        Parameters
        ----------
            value (float): lateral offset of the lane

            shape (DynamicsShapes): shape of the offset action

            maxlatacc (float): maximum allowed lateral acceleration

            continuous (bool): if the controller tries to keep the relative speed 
                Default: True

        Attributes
        ----------
            continuous (bool): if the controller tries to keep the relative speed 

            value (float): lateral offset of the lane

            target (str): the name of the entity (relative only)

            dynshape (DynamicsShapes): the shape of the action

            maxlatacc (float): maximum allowed lateral acceleration

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,shape,maxlatacc,continuous = True):
        """ initalizes the LaneOffsetAction
            Parameters
            ----------
                value (float): lateral offset of the lane

                shape (DynamicsShapes): shape of the offset action

                maxlatacc (float): maximum allowed lateral acceleration

                continuous (bool): if the controller tries to keep the relative speed 
                    Default: True
        """
        if not isinstance(continuous,bool):
            raise TypeError('continuous input not of type bool')

        self.continuous = continuous
        self.value = value
        if shape not in DynamicsShapes:
            raise ValueError(shape + '; is not a valid shape.')
        self.dynshape = shape
        self.maxlatacc = maxlatacc

    def get_attributes(self):
        """ returns the attributes of the LaneOffsetAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.value)
        return retdict
        
    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        element = ET.Element('PrivateAction')
        lataction = ET.SubElement(element,'LateralAction')
        laneoffsetaction = ET.SubElement(lataction,'LaneOffsetAction',attrib={'continuous':convert_bool(self.continuous)})
        ET.SubElement(laneoffsetaction,'LaneOffsetActionDynamics',{'maxLateralAcc':str(self.maxlatacc),'dynamicsShape':self.dynshape.name})
        laneoftarget = ET.SubElement(laneoffsetaction,'LaneOffsetTarget')
        ET.SubElement(laneoftarget,'AbsoluteTargetLaneOffset',self.get_attributes())

        return element

class RelativeLaneOffsetAction(_PrivateActionType):
    """ the RelativeLaneOffsetAction class creates a LateralAction of type LaneOffsetAction with a relative target
        
        Parameters
        ----------
            value (float): relative lateral offset of the target

            entity (str): name of the entity

            shape (str): shape of the offset action

            maxlatacc (float): maximum allowed lateral acceleration

            continuous (bool): if the controller tries to keep the relative speed 
                Default: True

        Attributes
        ----------
            continuous (bool): if the controller tries to keep the relative speed 

            value (float): relative lateral offset of the arget

            target (str): the name of the entity

            dynshape (str): the shape of the action

            maxlatacc (float): maximum allowed lateral acceleration

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,value,entity,shape,maxlatacc,continuous = True):
        """ initalizes the LaneOffsetAction,

            Parameters
            ----------
                value (float): relative lateral offset of the target

                entity (str): name of the entity

                shape (str): shape of the offset action

                maxlatacc (float): maximum allowed lateral acceleration

                continuous (bool): if the controller tries to keep the relative speed 
                    Default: True
        """
        if not isinstance(continuous,bool):
            raise TypeError('continuous input not of type bool')
        
        self.continuous = continuous
        self.value = value
        self.target = entity
        if shape not in DynamicsShapes:
            raise ValueError(shape + '; is not a valid shape.')
        self.dynshape = shape
        self.maxlatacc = maxlatacc

    def get_attributes(self):
        """ returns the attributes of the LaneOffsetAction as a dict

        """
        retdict = {}
        retdict['value'] = str(self.value)
        retdict['entityRef'] = self.target
        return retdict
        
    def get_element(self):
        """ returns the elementTree of the LaneOffsetAction

        """
        element = ET.Element('PrivateAction')
        lataction = ET.SubElement(element,'LateralAction')
        laneoffsetaction = ET.SubElement(lataction,'LaneOffsetAction',attrib={'continuous':convert_bool(self.continuous)})
        ET.SubElement(laneoffsetaction,'LaneOffsetActionDynamics',{'maxLateralAcc':str(self.maxlatacc),'dynamicsShape':self.dynshape.name})
        laneoftarget = ET.SubElement(laneoffsetaction,'LaneOffsetTarget')
        ET.SubElement(laneoftarget,'RelativeTargetLaneOffset',attrib=self.get_attributes())

        return element


class LateralDistanceAction(_PrivateActionType):
    """ 
        
        Parameters
        ----------
            entity (str): the target name

            distance (float): the lateral distance to the entity

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continuous (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None
            
        Attributes
        ----------
            entity (str): the target name

            distance (float): the lateral distance to the entity

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point

            continuous (bool): if the controller tries to keep the relative speed 

            distance (float): if the distance metric is used

            timegap (float): if timegap metric is used

            dynamic_constraint (DynamicsConstrains): Dynamics constraints of the action


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,entity,distance=None,freespace=True,continuous=True,max_acceleration = None,max_deceleration = None,max_speed = None):
        """ initalizes the LateralDistanceAction

        Parameters
        ----------
            entity (str): the target name

            distance (float): the lateral distance to the entity

            freespace (bool): (True) distance between bounding boxes, (False) distance between ref point
                Default: True

            continuous (bool): if the controller tries to keep the relative speed 
                Default: True

            max_acceleration (float): maximum acceleration allowed
                Default: None

            max_deceleration (float): maximum deceleration allowed
                Default: None

            max_speed (float): maximum speed allowed
                Default: None
        """
        self.distance = distance
        self.target = entity
        if not isinstance(continuous,bool):
            raise TypeError('continuous input not of type bool')

        if not isinstance(freespace,bool):
            raise TypeError('freespace input not of type bool')
        
        self.freespace = freespace
        self.continuous = continuous
        self.dynamic_constraint = DynamicsConstrains(max_acceleration,max_deceleration,max_speed)

    def get_attributes(self):
        """ returns the attributes of the LateralDistanceAction as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['freespace'] = convert_bool(self.freespace)
        retdict['continuous'] = convert_bool(self.continuous)
        if self.distance:
            retdict['distance'] = str(self.distance)
        return retdict

    def get_element(self):
        """ returns the elementTree of the LateralDistanceAction

        """
        element = ET.Element('PrivateAction')
        lataction = ET.SubElement(element,'LateralAction')
        lateraldistanceaction = ET.SubElement(lataction,'LateralDistanceAction',attrib=self.get_attributes())
        if self.dynamic_constraint.is_filled():
            lateraldistanceaction.append(self.dynamic_constraint.get_element())

        return element



# teleport
class TeleportAction(_PrivateActionType):
    """ the TeleportAction creates the Teleport action of OpenScenario
        
        Parameters
        ----------
            position (*Position): any position object

        Attributes
        ----------
            position (*Position): any position object


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,position):
        """ initalizes the TeleportAction

        Parameters
        ----------
            position (*Position): any position object

        """
        if not isinstance(position,_PositionType):
            raise TypeError('position input not a valid Position type')        

        self.position = position

    def get_element(self):
        """ returns the elementTree of the TeleportAction

        """
        element = ET.Element('PrivateAction')
        telact = ET.SubElement(element,'TeleportAction')
        telact.append(self.position.get_element())
        return element



# Routing actions

class AssignRouteAction(_PrivateActionType):
    """ AssignRouteAction creates a RouteAction of type AssignRouteAction

        Parameters
        ----------
            route (Route, or CatalogReference): the route to follow

        Attributes
        ----------
            route (Route, or CatalogReference): the route to follow


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,route):
        """ initalizes the AssignRouteAction

            Parameters
            ----------
                route (Route, or CatalogReference): the route to follow

        """
        if not ( isinstance(route,Route) or isinstance(route,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 

        self.route = route

    def get_element(self):
        """ returns the elementTree of the AssignRouteAction

        """
        element = ET.Element('PrivateAction')
        routeaction = ET.SubElement(element,'RoutingAction')
        assignrouteaction = ET.SubElement(routeaction,'AssignRouteAction')
        assignrouteaction.append(self.route.get_element())

        return element


class AcquirePositionAction(_PrivateActionType):
    """ AcquirePositionAction creates a RouteAction of type AcquirePositionAction
        
        Parameters
        ----------
            position (*Position): target position

        Attributes
        ----------
            position (*Position): target position

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,position):
        """ initalizes the AssignRouteAction

            Parameters
            ----------
                position (*Position): target position

        """
        if not isinstance(position,_PositionType):
            raise TypeError('position input not a valid Position type')        

        self.position = position

    def get_element(self):
        """ returns the elementTree of the AssignRouteAction

        """
        element = ET.Element('PrivateAction')
        routeaction = ET.SubElement(element,'RoutingAction')
        posaction = ET.SubElement(routeaction,'AcquirePositionAction')
        posaction.append(self.position.get_element())

        return element



class FollowTrajectoryAction(_PrivateActionType):
    """ FollowTrajectoryAction creates a RouteAction of type FollowTrajectoryAction

        Parameters
        ----------
            trajectory (Trajectory, or CatalogReference): the trajectory to follow

            following_mode (FollowMode): the following mode of the action

            reference_domain (ReferenceContext): how to follow
                Default: None
            scale (double): scalefactor of the timeings (must be combined with reference_domain and offset)
                Default: None
            offset (double): offset for time values (must be combined with reference_domain and scale)
                Default: None

        Attributes
        ----------
            trajectory (Trajectory, or CatalogReference): the trajectory to follow

            following_mode (str): the following mode of the action

            timeref (TimeReference): the time reference of the trajectory

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,trajectory,following_mode,reference_domain=None,scale=None,offset=None):
        """ initalize the FollowTrajectoryAction 

            Parameters
            ----------
                trajectory (Trajectory, or CatalogReference): the trajectory to follow

                following_mode (FollowMode): the following mode of the action

                reference_domain (str): absolute or relative time reference (must be combined with scale and offset)
                    Default: None
                scale (double): scalefactor of the timings (must be combined with reference_domain and offset)
                    Default: None
                offset (double): offset for time values (must be combined with reference_domain and scale)
                    Default: None
        """
        # if following_mode not in FollowMode:
        #     ValueError(str(following_mode) + ' is not a valied following mode.')
        if not ( isinstance(trajectory,Trajectory) or isinstance(trajectory,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 
        self.trajectory = trajectory
        self.following_mode = following_mode
        # TODO: check reference_domain
        self.timeref = TimeReference(reference_domain,scale,offset)

    def get_element(self):
        """ returns the elementTree of the AssignRouteAction

        """
        element = ET.Element('PrivateAction')
        routeaction = ET.SubElement(element,'RoutingAction')
        trajaction = ET.SubElement(routeaction,'FollowTrajectoryAction')
        trajaction.append(self.trajectory.get_element())
        trajaction.append(self.timeref.get_element())
        ET.SubElement(trajaction,'TrajectoryFollowingMode',attrib={'followingMode':self.following_mode.name})

        return element





class ActivateControllerAction(_PrivateActionType):
    """ ActivateControllerAction creates a ActivateControllerAction of open scenario
        
        Parameters
        ----------
            lateral (boolean): activate or deactivate the controller

            longitudinal (boolean): activate or deactivate the controller

        Attributes
        ----------
            lateral (boolean): activate or deactivate the controller
            
            longitudinal (boolean): activate or deactivate the controller

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,lateral, longitudinal):
        """ initalizes the ActivateControllerAction

            Parameters
            ----------
                lateral (boolean): activate or deactivate the controller
            
                longitudinal (boolean): activate or deactivate the controller

        """
        if not isinstance(lateral,bool):
            raise TypeError('lateral input is not of type bool') 
        if not isinstance(longitudinal,bool):
            raise TypeError('longitudinal input is not of type bool') 
        self.lateral = lateral
        self.longitudinal = longitudinal

    def get_attributes(self):
        """ returns the attributes of the ActivateControllerAction as a dict

        """
        return {'lateral':convert_bool(self.lateral),'longitudinal':convert_bool(self.longitudinal)}

    def get_element(self):
        """ returns the elementTree of the ActivateControllerAction

        """
        element = ET.Element('PrivateAction')
        ET.SubElement(element,'ActivateControllerAction',attrib=self.get_attributes())

        return element


class AssignControllerAction(_PrivateActionType):
    """ AssignControllerAction creates a ControllerAction of type AssignControllerAction
        
        Parameters
        ----------
            controller (Controller or Catalogreference): a controller to assign

        Attributes
        ----------
            controller (boolController or Catalogreferenceean): a controller to assign

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,controller):
        """ initalizes the AssignControllerAction

            Parameters
            ----------
                controller (Controller or Catalogreference): a controller to assign

        """
        if not ( isinstance(controller,Controller) or isinstance(controller,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 
        self.controller = controller

    def get_element(self):
        """ returns the elementTree of the AssignControllerAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerActiton')
        controlleraction.append(self.controller.get_element())

        return element


class OverrideThrottleAction(_PrivateActionType):
    """ OverrideThrottleAction creates a ControllerAction of type OverrideControllerValueAction and OverrideThrottleAction 
        
        Parameters
        ----------
            value (double): 0...1 throttle pedal

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 throttle pedal

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideThrottleAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        if not isinstance(activate,bool):
            raise TypeError('activate input is not of type bool')
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideThrottleAction as a dict

        """
        return {'value':str(self.value),'active':convert_bool(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideThrottleAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideThrottleAction',self.get_attributes())
        return element


class OverrideBrakeAction(_PrivateActionType):
    """ OverrideBrakeAction creates a ControllerAction of type OverrideControllerValueAction and OverrideBrakeAction 
        
        Parameters
        ----------
            value (double): 0...1 throttle pedal

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideBrakeAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        if not isinstance(activate,bool):
            raise TypeError('activate input is not of type bool')
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideBrakeAction as a dict

        """
        return {'value':str(self.value),'active':convert_bool(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideBrakeAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideBrakeAction',self.get_attributes())
        return element


class OverrideClutchAction(_PrivateActionType):
    """ OverrideClutchAction creates a ControllerAction of type OverrideControllerValueAction and OverrideClutchAction
        
        Parameters
        ----------
            value (double): 0...1 clutch pedal value

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideClutchAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        if not isinstance(activate,bool):
            raise TypeError('activate input is not of type bool')
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideClutchAction as a dict

        """
        return {'value':str(self.value),'active':convert_bool(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideClutchAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideClutchAction',self.get_attributes())
        return element



class OverrideParkingBrakeAction(_PrivateActionType):
    """ OverrideParkingBrakeAction creates a ControllerAction of type OverrideControllerValueAction and OverrideParkingBrakeAction 
        
        Parameters
        ----------
            value (double): 0...1 clutch pedal value

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideParkingBrakeAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        if not isinstance(activate,bool):
            raise TypeError('activate input is not of type bool')
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideParkingBrakeAction as a dict

        """
        return {'value':str(self.value),'active':convert_bool(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideParkingBrakeAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideParkingBrakeAction',self.get_attributes())
        return element




class OverrideSteeringWheelAction(_PrivateActionType):
    """ OverrideSteeringWheelAction creates a ControllerAction of type OverrideControllerValueAction and OverrideSteeringWheelAction 
        
        Parameters
        ----------
            value (double): 0...1 clutch pedal value

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideSteeringWheelAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        if not isinstance(activate,bool):
            raise TypeError('activate input is not of type bool')
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideSteeringWheelAction as a dict

        """
        return {'value':str(self.value),'active':convert_bool(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideSteeringWheelAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideSteeringWheelAction',self.get_attributes())
        return element



class OverrideGearAction(_PrivateActionType):
    """ OverrideGearAction creates a ControllerAction of type OverrideControllerValueAction and OverrideGearAction 
        
        Parameters
        ----------
            value (double): 0...1 clutch pedal value

            active (boolean): overide (True) or stop override (False)

        Attributes
        ----------
            value (double): 0...1 brake pedal value

            active (boolean): overide (True) or stop override (False)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,value, activate):
        """ initalizes the OverrideGearAction

            Parameters
            ----------
                value (double): 0...1 throttle pedal

                active (boolean): overide (True) or stop override (False)

        """
        self.value = value
        if not isinstance(activate,bool):
            raise TypeError('activate input is not of type bool')
        self.activate = activate

    def get_attributes(self):
        """ returns the attributes of the OverrideGearAction as a dict

        """
        return {'value':str(self.value),'active':convert_bool(self.activate)}

    def get_element(self):
        """ returns the elementTree of the OverrideGearAction

        """
        element = ET.Element('PrivateAction')
        controlleraction = ET.SubElement(element,'ControllerAction')
        overrideaction = ET.SubElement(controlleraction,'OverrideControllerValueAction')
        ET.SubElement(overrideaction,'OverrideGearAction',self.get_attributes())
        return element



class VisibilityAction(_PrivateActionType):
    """ creates a VisibilityAction
        
        Parameters
        ----------
            graphics (boolean): visible for graphics or not

            traffic (boolean): visible for traffic

            sensors (boolean): visible to sensors or not

        Attributes
        ----------
            graphics (boolean): visible for graphics or not

            traffic (boolean): visible for traffic

            sensors (boolean): visible to sensors or not

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,graphics, traffic, sensors):
        """ initalizes the VisibilityAction

            Parameters
            ----------
            graphics (boolean): visible for graphics or not

            traffic (boolean): visible for traffic

            sensors (boolean): visible to sensors or not

        """
        if not isinstance(graphics,bool):
            raise TypeError('graphics input is not of type bool')
        if not isinstance(traffic,bool):
            raise TypeError('traffic input is not of type bool')
        if not isinstance(sensors,bool):
            raise TypeError('sensors input is not of type bool')
        self.graphics = graphics
        self.traffic = traffic
        self.sensors = sensors

    def get_attributes(self):
        """ returns the attributes of the VisibilityAction as a dict

        """
        return {'graphics':convert_bool(self.graphics),'active':convert_bool(self.traffic),'sensors':convert_bool(self.sensors)}

    def get_element(self):
        """ returns the elementTree of the VisibilityAction

        """
        element = ET.Element('PrivateAction')
        ET.SubElement(element,'VisibilityAction',self.get_attributes())
        return element

class AbsoluteSynchronizeAction(_PrivateActionType):
    """ creates a SynchronizeAction with an absolute speed as target speed
        
        Parameters
        ----------
            entity (str): entity to syncronize with

            entity_PositionType (*Position): the position of the entity to syncronize to

            target_PositionType (*Position): the position of the target that should syncronize

            speed (double): the absolute speed of the target that should syncronize

            target_tolerance_master (optional) (double): tolerance offset of the master's position [m]. Not officially part of OpenSCENARIO but supported in esmini

            target_tolerance (optional) (double): tolerance offset of the target's position [m]. Not officially part of OpenSCENARIO but supported in esmini

        Attributes
        ----------
            entity (str): entity to syncronize with

            entity_PositionType (*Position): the position of the entity to syncronize to

            target_PositionType (*Position): the position of the target that should syncronize

            speed (double): the absolute speed of the target that should syncronize

            target_tolerance_master (optional) (double): tolerance offset of the master's position [m]. Not officially part of OpenSCENARIO but supported in esmini

            target_tolerance (optional) (double): tolerance offset of the target's position [m]. Not officially part of OpenSCENARIO but supported in esmini

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,entity,entity_PositionType,target_PositionType,speed,target_tolerance_master=None,target_tolerance=None):
        """ initalize the AbsoluteSynchronizeAction

            Parameters
            ----------
                entity (str): entity to syncronize with

                entity_PositionType (*Position): the position of the entity to syncronize to

                target_PositionType (*Position): the position of the target that should syncronize

                speed (double): the absolute speed of the target that should syncronize

                target_tolerance_master (optional) (double): tolerance offset of the master's position [m]. Not officially part of OpenSCENARIO but supported in esmini

                target_tolerance (optional) (double): tolerance offset of the target's position [m]. Not officially part of OpenSCENARIO but supported in esmini
        """

        self.entity = entity
        if not isinstance(entity_PositionType,_PositionType):
            raise TypeError('entity_PositionType input is not a valid Position')
        
        if not isinstance(target_PositionType,_PositionType):
            raise TypeError('target_PositionType input is not a valid Position')
        self.entity_PositionType = entity_PositionType
        self.target_PositionType = target_PositionType
        self.speed = speed
        self.target_tolerance_master = target_tolerance_master
        self.target_tolerance = target_tolerance

    def get_attributes(self):
        """ returns the attributes of the AbsoluteSynchronizeAction as a dict

        """
        attr = {'masterEntityRef':self.entity}
        if self.target_tolerance_master is not None:
            attr.update({'targetToleranceMaster': str(self.target_tolerance_master)})
        if self.target_tolerance is not None:
            attr.update({'targetTolerance': str(self.target_tolerance)})
        return attr

    def get_element(self):
        """ returns the elementTree of the AbsoluteSynchronizeAction

        """
        element = ET.Element('PrivateAction')
        syncaction = ET.SubElement(element,'SynchronizeAction',self.get_attributes())
        syncaction.append(self.entity_PositionType.get_element('TargetPositionMaster'))
        syncaction.append(self.target_PositionType.get_element('TargetPosition'))
        finalspeed = ET.SubElement(syncaction,'FinalSpeed')
        ET.SubElement(finalspeed,'AbsoluteSpeed',attrib={'value':str(self.speed)})
        
        return element


class RelativeSynchronizeAction(_PrivateActionType):
    """ creates a SynchronizeAction with a relative speed target
        
        Parameters
        ----------
            entity (str): entity to syncronize with

            entity_PositionType (*Position): the position of the entity to syncronize to

            target_PositionType (*Position): the position of the target that should syncronize

            speed (double): the relative speed of the target that should syncronize

            speed_target_type (str): the semantics of the value (delta, factor)

            target_tolerance_master (optional) (double): tolerance offset of the master's position [m]. Not officially part of OpenSCENARIO but supported in esmini

            target_tolerance (optional) (double): tolerance offset of the target's position [m]. Not officially part of OpenSCENARIO but supported in esmini

        Attributes
        ----------
            entity (str): entity to syncronize with

            entity_PositionType (*Position): the position of the entity to syncronize to

            target_PositionType (*Position): the position of the target that should syncronize

            speed (double): the relative speed of the target that should syncronize

            speed_target_type (str): the semantics of the value (delta, factor)

            target_tolerance_master (optional) (double): tolerance offset of the master's position [m]. Not officially part of OpenSCENARIO but supported in esmini

            target_tolerance (optional) (double): tolerance offset of the target's position [m]. Not officially part of OpenSCENARIO but supported in esmini

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the the attributes of the class

    """
    def __init__(self,entity,entity_PositionType,target_PositionType,speed,speed_target_type,target_tolerance_master=None,target_tolerance=None):
        """ initalize the RelativeSynchronizeAction
    
            Parameters
            ----------
                entity (str): entity to syncronize with

                entity_PositionType (*Position): the position of the entity to syncronize to

                target_PositionType (*Position): the position of the target that should syncronize

                speed (double): the absolute speed of the target that should syncronize

                speed_target_type (str): the semantics of the value (delta, factor)

                target_tolerance_master (optional) (double): tolerance offset of the master's position [m]. Not officially part of OpenSCENARIO but supported in esmini

                target_tolerance (optional) (double): tolerance offset of the target's position [m]. Not officially part of OpenSCENARIO but supported in esmini
        """

        self.entity = entity
        if not isinstance(entity_PositionType,_PositionType):
            raise TypeError('entity_PositionType input is not a valid Position')
        
        if not isinstance(target_PositionType,_PositionType):
            raise TypeError('target_PositionType input is not a valid Position')
        self.entity_PositionType = entity_PositionType
        self.target_PositionType = target_PositionType
        self.speed = speed
        # if speed_target_type not in SpeedTargetValueType:
            # ValueError(speed_target_type + ' is not a valid speed_target_type')
        self.speed_target_type = speed_target_type
        self.target_tolerance_master = target_tolerance_master
        self.target_tolerance = target_tolerance

    def get_attributes(self):
        """ returns the attributes of the VisibilityAction as a dict

        """
        attr = {'masterEntityRef':self.entity}
        if self.target_tolerance_master is not None:
            attr.update({'targetToleranceMaster': str(self.target_tolerance_master)})
        if self.target_tolerance is not None:
            attr.update({'targetTolerance': str(self.target_tolerance)})
        return attr

    def get_element(self):
        """ returns the elementTree of the VisibilityAction

        """
        element = ET.Element('PrivateAction')
        syncaction = ET.SubElement(element,'SynchronizeAction',self.get_attributes())
        syncaction.append(self.entity_PositionType.get_element('TargetPositionMaster'))
        syncaction.append(self.target_PositionType.get_element('TargetPosition'))
        finalspeed = ET.SubElement(syncaction,'FinalSpeed')
        ET.SubElement(finalspeed,'RelativeSpeedToMaster',attrib={'value':str(self.speed),'speedTargetValueType':self.speed_target_type})
        
        return element


#### Global Actions ####


class ParameterAddAction(_ActionType):
    """ The ParameterAddAction class creates a ParameterAction of type ParameterModifyAction which adds a value to an existing Parameter
        
        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        Attributes
        ----------

            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,parameter_ref,value):
        """ initalize the ParameterAddAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value
    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        paramaction = ET.SubElement(element,'ParameterAction',{'parameterRef':self.parameter_ref})
        modifaction = ET.SubElement(paramaction,'ModifyAction')
        rule = ET.SubElement(modifaction,'Rule')
        ET.SubElement(rule,'AddValue',self.get_attributes())

        
        return element


class ParameterMultiplyAction(_ActionType):
    """ The ParameterMultiplyAction class creates a ParameterAction of tyoe ParameterModifyAction which adds a value to an existing Parameter
        
        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be multiplied to the parameter

        Attributes
        ----------

            parameter_ref (str): name of the parameter

            value (double): the value that should be multiplied to the parameter

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,parameter_ref,value):
        """ initalize the ParameterMultiplyAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value
    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        paramaction = ET.SubElement(element,'ParameterAction',{'parameterRef':self.parameter_ref})
        modifaction = ET.SubElement(paramaction,'ModifyAction')
        rule = ET.SubElement(modifaction,'Rule')
        ET.SubElement(rule,'MultiplyByValue',self.get_attributes())

        return element


class ParameterSetAction(_ActionType):
    """ The ParameterSetAction class creates a ParameterAction which adds a value to an existing Parameter
        
        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be set to the parameter

        Attributes
        ----------

            parameter_ref (str): name of the parameter

            value (double): the value that should be set to the parameter

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,parameter_ref,value):
        """ initalize the ParameterSetAction

        Parameters
        ----------
            parameter_ref (str): name of the parameter

            value (double): the value that should be added to the parameter

        """
        self.parameter_ref = parameter_ref
        self.value = value
    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        paramaction = ET.SubElement(element,'ParameterAction',{'parameterRef':self.parameter_ref})
        ET.SubElement(paramaction,'SetAction',self.get_attributes())
        
        return element


class TrafficSignalStateAction(_ActionType):
    """ The TrafficSignalStateAction class creates a Infrastructure action which controls the state of a traffic signal
        
        Parameters
        ----------
            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        Attributes
        ----------

            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,name,state):
        """ initalize the TrafficSignalStateAction

        Parameters
        ----------
            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        """
        self.name = name
        self.state = state

    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'name':self.name,'state':self.state}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        infra = ET.SubElement(element,'InfrastructureAction')
        tsa = ET.SubElement(infra,'TrafficSignalAction')
        ET.SubElement(tsa,'TrafficSignalStateAction',self.get_attributes())
        
        return element


class AddEntityAction(_ActionType):
    """ The AddEntityAction class creates a EntityAction which adds a entity to the scenario
        
        Parameters
        ----------
            entityref (str): reference name of the newly added vehicle

            position (*Position): position where the vehicle should be added

        Attributes
        ----------

            entityref (str): reference name of the newly added vehicle

            position (*Position): position where the vehicle should be added

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,entityref,position):
        """ initalize the AddEntityAction

        Parameters
        ----------
            entityref (str): reference name of the newly added vehicle

            position (*Position): position where the vehicle should be added

        """
        
        self.entityref = entityref
        self.position = position

    def get_attributes(self):
        """ returns the attributes of the AddEntityAction as a dict

        """
        return {'entityRef':self.entityref}

    def get_element(self):
        """ returns the elementTree of the AddEntityAction

        """
        element = ET.Element('GlobalAction')
        entityact = ET.SubElement(element,'EntityAction',attrib=self.get_attributes())
        addentity = ET.SubElement(entityact,'AddEntityAction')
        addentity.append(self.position.get_element())
        
        
        return element



class DeleteEntityAction(_ActionType):
    """ The DeleteEntityAction class creates a EntityAction which removes a entity to the scenario
        
        Parameters
        ----------
            entityref (str): reference name of the vehicle to remove

        Attributes
        ----------

            entityref (str): reference name of the vehicle to remove


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,entityref):
        """ initalize the DeleteEntityAction

        Parameters
        ----------
            entityref (str): reference name of the vehicle to remove

        """
        
        self.entityref = entityref

    def get_attributes(self):
        """ returns the attributes of the DeleteEntityAction as a dict

        """
        return {'entityRef':self.entityref}

    def get_element(self):
        """ returns the elementTree of the DeleteEntityAction

        """
        element = ET.Element('GlobalAction')
        entityact = ET.SubElement(element,'EntityAction',attrib=self.get_attributes())
        ET.SubElement(entityact,'DeleteEntityAction')

        
        
        return element



class TrafficSignalControllerAction(_ActionType):
    """ The TrafficSignalControllerAction class creates a Infrastructure action which activates a controller of a traffic signal
        
        Parameters
        ----------
            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        Attributes
        ----------

            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,name,state):
        """ initalize the TrafficSignalStateAction

        Parameters
        ----------
            name (str): id of the signal in the road network

            state (str): the state to set to the traffic light

        """
        self.name = name
        self.state = state

    def get_attributes(self):
        """ returns the attributes of the AbsoluteSpeedAction as a dict

        """
        return {'name':self.name,'state':self.state}

    def get_element(self):
        """ returns the elementTree of the AbsoluteSpeedAction

        """
        element = ET.Element('GlobalAction')
        infra = ET.SubElement(element,'InfrastructureAction')
        tsa = ET.SubElement(infra,'TrafficSignalAction')
        ET.SubElement(tsa,'TrafficSignalStateAction',self.get_attributes())
        
        return element


class TrafficSourceAction(_ActionType):
    """ The TrafficSourceAction class creates a TrafficAction of the typ TrafficSourceAction
        
        Parameters
        ----------
            rate (float): rate of appearing traffic

            radius (float): the radius of the source around the position

            position (*Position): any Position to define the source

            trafficdefinition (TrafficDefinition): definition of the traffic

            velocity (float): optional starting velocity of the traffic
                Default: None

        Attributes
        ----------

            rate (float): rate of appearing traffic

            radius (float): the radius of the source around the position

            position (*Position): any Position to define the source

            trafficdefinition (TrafficDefinition): definition of the traffic

            velocity (float): optional starting velocity of the traffic
                Default: None


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,rate,radius,position,trafficdefinition,velocity = None):
        """ initalize the TrafficSourceAction

        Parameters
        ----------
            rate (float): rate of appearing traffic

            radius (float): the radius of the source around the position

            position (*Position): any Position to define the source

            trafficdefinition (TrafficDefinition): definition of the traffic

            velocity (float): optional starting velocity of the traffic
                Default: None

        """
        self.rate = rate
        self.radius = radius
        if not isinstance(position,_PositionType):
            raise TypeError('position input is not a valid Position')
        
        if not isinstance(trafficdefinition,TrafficDefinition):
            raise TypeError('trafficdefinition input is not of type TrafficDefinition')
        self.position = position
        self.trafficdefinition = trafficdefinition
        self.velocity = velocity

    def get_attributes(self):
        """ returns the attributes of the TrafficSourceAction as a dict

        """
        retdict = {}
        retdict['rate'] = str(self.rate)
        retdict['radius'] = str(self.radius)
        if self.velocity:
            retdict['velocity'] = str(self.velocity)
        return retdict

    def get_element(self):
        """ returns the elementTree of the TrafficSourceAction

        """
        element = ET.Element('GlobalAction')
        trafficaction = ET.SubElement(element, 'TrafficAction')
        sourceaction = ET.SubElement(trafficaction,'TrafficSourceAction',attrib=self.get_attributes())
        sourceaction.append(self.position.get_element())
        sourceaction.append(self.trafficdefinition.get_element())

        
        
        return element


class TrafficSinkAction(_ActionType):
    """ The TrafficSinkAction class creates a TrafficAction of the typ TrafficSinkAction
        
        Parameters
        ----------
            rate (float): rate of appearing traffic

            radius (float): the radius of the sink around the position

            position (*Position): any Position to define the sink

            trafficdefinition (TrafficDefinition): definition of the traffic

        Attributes
        ----------

            rate (float): rate of appearing traffic

            radius (float): the radius of the source around the position

            position (*Position): any Position to define the source

            trafficdefinition (TrafficDefinition): definition of the traffic

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,rate,radius,position,trafficdefinition):
        """ initalize the TrafficSinkAction

        Parameters
        ----------
            rate (float): rate of appearing traffic

            radius (float): the radius of the source around the position

            position (*Position): any Position to define the source

            trafficdefinition (TrafficDefinition): definition of the traffic

        """
        self.rate = rate
        self.radius = radius
        if not isinstance(position,_PositionType):
            raise TypeError('position input is not a valid Position')
        
        if not isinstance(trafficdefinition,TrafficDefinition):
            raise TypeError('trafficdefinition input is not of type TrafficDefinition')
        self.position = position
        self.trafficdefinition = trafficdefinition


    def get_attributes(self):
        """ returns the attributes of the TrafficSinkAction as a dict

        """
        retdict = {}
        retdict['rate'] = str(self.rate)
        retdict['radius'] = str(self.radius)
        return retdict

    def get_element(self):
        """ returns the elementTree of the TrafficSinkAction

        """

        element = ET.Element('GlobalAction')
        trafficaction = ET.SubElement(element, 'TrafficAction')
        sinkaction = ET.SubElement(trafficaction,'TrafficSinkAction',attrib=self.get_attributes())
        sinkaction.append(self.position.get_element())
        sinkaction.append(self.trafficdefinition.get_element())

        return element


class TrafficSwarmAction(_ActionType):
    """ The TrafficSwarmAction class creates a TrafficAction of the typ TrafficSwarmAction
        
        Parameters
        ----------
            semimajoraxis (float): half length of major axis of ellipsis around target

            semiminoraxis (float): half length of minor axis of ellipsis around target

            innerradius (float): radius of inner cirvle

            offset (float): longitudinal offset from central entity

            numberofvehicles (int): maximum number of vehicles around entity

            centralobject (str): entity to swarm around

            trafficdefinition (TrafficDefinition): definition of the traffic

            velocity (float): optional starting velocity
                Default: None
        Attributes
        ----------

            semimajoraxis (float): half length of major axis of ellipsis around target

            semiminoraxis (float): half length of minor axis of ellipsis around target

            innerradius (float): radius of inner cirvle

            offset (float): longitudinal offset from central entity

            numberofvehicles (int): maximum number of vehicles around entity

            centralobject (str): entity to swarm around

            trafficdefinition (TrafficDefinition): definition of the traffic

            velocity (float): optional starting velocity
                Default: None

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self,semimajoraxis,semiminoraxis,innerradius,offset,numberofvehicles,centralobject,trafficdefinition,velocity = None):
        """ initalize the TrafficSinkAction

        Parameters
        ----------
            semimajoraxis (float): half length of major axis of ellipsis around target

            semiminoraxis (float): half length of minor axis of ellipsis around target

            innerradius (float): radius of inner circle

            offset (float): longitudinal offset from central entity

            numberofvehicles (int): maximum number of vehicles around entity

            centralobject (str): entity to swarm around

            trafficdefinition (TrafficDefinition): definition of the traffic

            velocity (float): optional starting velocity
                Default: None
        """
        self.semimajoraxis = semimajoraxis
        self.semiminoraxis = semiminoraxis
        self.innerradius = innerradius
        self.offset = offset
        self.numberofvehicles = numberofvehicles
        self.centralobject = centralobject
        if not isinstance(trafficdefinition,TrafficDefinition):
            raise TypeError('trafficdefinition input is not of type TrafficDefinition')
        self.trafficdefinition = trafficdefinition
        self.velocity = velocity

    def get_attributes(self):
        """ returns the attributes of the TrafficSinkAction as a dict

        """
        retdict = {}
        retdict['semiMajorAxis'] = str(self.semimajoraxis)
        retdict['semiMinorAxis'] = str(self.semiminoraxis)
        retdict['innerRadius'] = str(self.innerradius)
        retdict['offset'] = str(self.offset)
        retdict['numberOfVehicles'] = str(self.numberofvehicles)
        if self.velocity:
            retdict['velocity'] = str(self.velocity)
        return retdict

    def get_element(self):
        """ returns the elementTree of the TrafficSinkAction

        """
        element = ET.Element('GlobalAction')
        trafficaction = ET.SubElement(element, 'TrafficAction')
        swarmaction = ET.SubElement(trafficaction,'TrafficSwarmAction',attrib=self.get_attributes())
        swarmaction.append(self.trafficdefinition.get_element())
        ET.SubElement(swarmaction,'CentralSwarmObject',attrib={'entityRef':self.centralobject})

        return element


class EnvironmentAction(_ActionType):
    """ The EnvironmentAction class creates a GlobalAction of the typ EnvironmentAction
        
        Parameters
        ----------
            name (str): name of the action

            environment (Environment or CatalogReference): the environment to change to

        Attributes
        ----------

            name (str): name of the action

            environment (Environment or CatalogReference): the environment to change to

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """
    def __init__(self, name, environment):
        """ initalize the EnvironmentAction

            Parameters
            ----------
                name (str): name of the action

                environment (Environment or CatalogReference): the environment to change to

        """
        self.name = name
        if not ( isinstance(environment,Environment) or isinstance(environment,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 
        self.environment = environment


    def get_attributes(self):
        """ returns the attributes of the EnvironmentAction as a dict

        """
        retdict = {}
        retdict['name'] = self.name
        return retdict

    def get_element(self):
        """ returns the elementTree of the EnvironmentAction

        """
        element = ET.Element('GlobalAction')
        envaction = ET.SubElement(element, 'EnvironmentAction')
        envaction.append(self.environment.get_element())
        
        return element


class CustomCommandAction(_ActionType):
    """ The CustomCommandAction creates a simulator defined action, can add any number of xml.etree.ElementTree to an Action

        NOTE: this is a very crude implementation, and the element has to be created by the user.
        
        Parameters
        ----------
            
        Attributes
        ----------

            elements (list of xml.etree.ElementTree): elements to add to the action

        Methods
        -------
            add_element(element)
                Adds an element to the action
            get_element()
                Returns the full ElementTree of the class

    """

    def __init__(self,semimajoraxis,semiminoraxis,innerradius,offset,numberofvehicles,centralobject,trafficdefinition,velocity = None):
        """ initalize the CustomCommandAction

            Parameters
            ----------

        """
        self.elements = []

    def add_element(self,element):
        """ adds an element to the CustomCommandAction

            Parameters
            ----------
                element (xml.etree.ElementTree): the element to add
        """
        self.elements.append(element)

    def get_element(self):
        """ returns the elementTree of the CustomCommandAction

        """
        element = ET.Element('UserDefinedAction')
        for e in self.elements:
            element.append(e)

        return element