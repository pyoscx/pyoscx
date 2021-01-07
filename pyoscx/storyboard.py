import xml.etree.ElementTree as ET

from .actions import _Action, _ActionType, _PrivateActionType

from .triggers import EmptyTrigger, ValueTrigger, SimulationTimeCondition
from .utils import EntityRef, _TriggerType, _EntityTriggerType, _ValueTriggerType
from .utils import ParameterDeclarations, CatalogFile, convert_bool
from .enumerations import Priority, Rule, ConditionEdge



class Init():
    """ the Init class, creates the init part of the storyboard
        
        Attributes
        ----------
            initactions (dir: {entityname: Action}): a directory 
                containing all init actions of the scenario
                
        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            add_init_action(entityname, action):
                adds a private action to the init

            add_global_action(action):
                adds a global action to the init

            add_user_defined_action(action):
                adds a user defined action to the init

    """
    def __init__(self):
        """ initalize the Init class

        """
        self.initactions = {}
        self.global_actions = []
        self.user_defined_actions = []

    def add_init_action(self,entityname,action):
        """ add_init_action adds an Private Action to the init.

        Parameters
        ----------
            entityname (str): name of the entity to add the action to
            action (*Action): Any private action to be added (like TeleportAction)
            
        """
        if not isinstance(action,_PrivateActionType):
            if isinstance(action,_ActionType):
                raise TypeError('the action provided is a global action, please use add_global_action instead')
            raise TypeError('action input is not a valid action')
        if entityname not in self.initactions:
            self.initactions[entityname] = []

        self.initactions[entityname].append(action)

    def add_global_action(self,action):
        """ add_global_action adds a global action to the init

        Parameters
        ----------
            action (*Action): any global action to add to the init

        """
        if isinstance(action,_PrivateActionType):
            raise TypeError('action input is a Private action, please use add_init_action instead')
        if not isinstance(action,_ActionType):
            raise TypeError('action input is not a valid action')
        self.global_actions.append(action)
    
    def add_user_defined_action(self,action):
        """ add_user_defined_action adds a userDefined action to the init

        Parameters
        ----------
            action (CustomCommandAction): a custom command action (NOTE: a very crude implementation see actions.py)

        """
        # NOTE: since this is not really implemented no checkes are done here.
        self.user_defined_actions.append(action)

    def get_element(self):
        """ returns the elementTree of the Init

        """
        element = ET.Element('Init')
        actions = ET.SubElement(element,'Actions')
        
        # add global actions
        for i in self.global_actions:
            actions.append(i.get_element())

        # add user defined actions
        for i in self.user_defined_actions:
            actions.append(i.get_element())

        # add private actions
        for i in self.initactions:
            private = ET.SubElement(actions,'Private',attrib={'entityRef':i})
            for j in self.initactions[i]:
                private.append(j.get_element())

        return element

class StoryBoard():
    """ The StoryBoard class creates the storyboard of OpenScenario
        
        Parameters
        ----------
            init (Init): the init part of the storyboard

            stoptrigger (Valuetrigger, Entitytrigger or EmptyTrigger): 
                the stoptrigger of the storyboard (optional)
                Default (EmptyTrigger) 

        Attributes
        ----------

            init (Init): the init of the storyboard

            stoptrigger (Valuetrigger, Entitytrigger or EmptyTrigger): 
                the stoptrigger

            stories (list of Story): all stories of the scenario

        Methods
        -------
            add_story (story)
                adds a story to the storyboard

            get_element()
                Returns the full ElementTree of the class


    """
    def __init__(self,init=Init(),stoptrigger=EmptyTrigger('stop')):
        """ initalizes the storyboard

        Parameters
        ----------
            init (Init): the init part of the storyboard
                Default: Init()

            stoptrigger (Valuetrigger, Entitytrigger, Trigger, ConditionGroup or EmptyTrigger): 
                the stoptrigger of the storyboard (optional)
                Default: (EmptyTrigger) 

        """
        if not isinstance(init,Init):
            raise TypeError('init is not of type Init')
        if not isinstance(stoptrigger,_TriggerType):
            raise TypeError('stoptrigger is not a valid Trigger')
        # check that the stoptrigger has a triggeringpoint that is 'stop'
        if stoptrigger._triggerpoint == 'StartTrigger':
            raise ValueError('the stoptrigger provided does not have stop as the triggeringpoint')
        self.init = init
        self.stoptrigger = stoptrigger
        self.stories = []

    def add_story(self,story):
        """ adds a story to the storyboard

        Parameters
        ----------
            story (Story): the story to be added 

        """
        if not isinstance(story,Story):
            raise TypeError('story input is not of type Story')
        self.stories.append(story)

    def add_act(self,act,parameters=ParameterDeclarations()):
        """ add_act is a quick way to add a single act to one story, for multi act type of scenarios, use Story instead.
    
            NOTE: if used multiple times multiple stories will be created

            Parameters
            ----------
                act (Act): the Act to add

                parameters (ParameterDeclarations): the parameters of the story (optional)
                    Default: ParameterDeclarations()
        """
        if not isinstance(act,Act):
            raise TypeError('act input is not of type Act')
        newstory = Story('story_' + act.name,parameters)
        newstory.add_act(act)
        self.stories.append(newstory)

    def add_maneuver_group(self,maneuvergroup,starttrigger=None,stoptrigger=EmptyTrigger('stop'),parameters=ParameterDeclarations()):
        """ add_maneuver_group is a quick way to add a single maneuver_group to one story, for multi maneuver_group type of scenarios, use Act instead.
    
            NOTE: if used multiple times multiple stories will be created

            Parameters
            ----------
                maneuvergroup (ManeuverGroup): the ManeuverGroup to add

                starttrigger (Valuetrigger, Entitytrigger, Trigger, ConditionGroup or EmptyTrigger): starttrigger for the act
                    Default: at simulationtime 0

                stoptrigger (Valuetrigger, Entitytrigger, Trigger, ConditionGroup or EmptyTrigger): stoptrigger for the act
                    Default: EmptyTrigger('stop')

                parameters (ParameterDeclarations): the parameters of the story (optional)
                    Default: ParameterDeclarations()

        """
        if not isinstance(maneuvergroup,ManeuverGroup):
            raise TypeError('maneuvergroup input is not of type ManeuverGroup')
        if starttrigger == None:
            starttrigger = ValueTrigger('act_start',0,ConditionEdge.rising,SimulationTimeCondition(0,Rule.greaterThan))
        elif starttrigger._triggerpoint == 'StopTrigger':
            raise ValueError('the starttrigger provided does not have start as the triggeringpoint')

        if stoptrigger._triggerpoint == 'StartTrigger':
            raise ValueError('the stoptrigger provided is not of type StopTrigger')
        newact = Act('act_' + maneuvergroup.name,starttrigger,stoptrigger)
        newact.add_maneuver_group(maneuvergroup)
        self.add_act(newact,parameters)


    def add_maneuver(self,maneuver,actors,starttrigger=None,stoptrigger=EmptyTrigger('stop'),parameters=ParameterDeclarations()):
        """ add_maneuver is a quick way to add a single maneuver to one story, for multi maneuver type of scenarios, use ManeuverGroup instead.
    
            NOTE: if used multiple times multiple stories will be created

            Parameters
            ----------
                maneuver (Maneuver): the Maneuver to add

                actors (list of 'str', or 'str'): list of all actors in the maneuver or just a name of the actor

                starttrigger (Valuetrigger, Entitytrigger, Trigger, ConditionGroup or EmptyTrigger): starttrigger for the act
                    Default: at simulationtime 0

                stoptrigger (Valuetrigger, Entitytrigger, Trigger, ConditionGroup or EmptyTrigger): stoptrigger for the act
                    Default: EmptyTrigger('stop')

                parameters (ParameterDeclarations): the parameters of the story (optional)
                    Default: ParameterDeclarations()

        """
        if not isinstance(maneuver,Maneuver):
            raise TypeError('maneuver input is not of type Maneuver')
        mangr = ManeuverGroup("maneuvuergroup_" + maneuver.name)
        if isinstance(actors,list):
            for a in actors:
                mangr.add_actor(a)
        else:
            mangr.add_actor(actors)
        mangr.add_maneuver(maneuver)
        self.add_maneuver_group(mangr,starttrigger=starttrigger,stoptrigger=stoptrigger,parameters=parameters)

    def get_element(self):
        """ returns the elementTree of the Storyboard

        """
        element = ET.Element('Storyboard')
        element.append(self.init.get_element())
        # if not self.stories:
        #     raise ValueError('no stories available for storyboard')
        
        if not self.stories:
            self.add_maneuver_group(ManeuverGroup('empty'),EmptyTrigger())
        for story in self.stories:
            element.append(story.get_element())
                
        element.append(self.stoptrigger.get_element())

        return element
    

class Story():
    """ The Story class creates a story of the OpenScenario
        
        Parameters
        ---------- 
            name (str): name of the story

            parameters (ParameterDeclarations): the parameters of the Story
                Default: ParameterDeclarations()
            
        Attributes
        ----------
            name (str): name of the story

            parameters (ParameterDeclarations): the parameters of the story (optional)

            acts (list of Act): all acts belonging to the story

        Methods
        -------
            add_act(act)
                adds an act to the story

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self, name, parameters=ParameterDeclarations()):
        """ initalizes the Story class

        Parameters
        ---------- 
            name (str): name of the story

            parameters (ParameterDeclarations): the parameters of the Story
        """
        self.name = name

        self.acts = []
        if not isinstance(parameters,ParameterDeclarations):
            raise TypeError('parameters input is not of type ParameterDeclarations')

        self.parameter = parameters

    def add_act(self,act):
        """ adds an act to the story

        Parameters
        ---------- 
            act (Act): act to add to the story

        """
        if not isinstance(act,Act):
            raise TypeError('act input is not of type Act')
        self.acts.append(act)

    def get_attributes(self):
        """ returns the attributes as a dict of the Story

        """
        return {'name':self.name}
    
    def get_element(self):
        """ returns the elementTree of the Story

        """
        element = ET.Element('Story',attrib=self.get_attributes())
        element.append(self.parameter.get_element())
        if not self.acts:
            raise ValueError('no acts added to the story')
        for a in self.acts:
            element.append(a.get_element())
        return element

class Act():
    """ the Act class creates the Act of the OpenScenario
        
        Parameters
        ----------
            name (str): name of the act

            starttrigger (*Trigger): starttrigger of the act
                Default: ValueTrigger('act_start',0,ConditionEdge.none,SimulationTimeCondition(0,Rule.greaterThan))

            stoptrigger (*Trigger): stoptrigger of the act (optional)
            
        Attributes
        ----------
            name (str): name of the act

            starttrigger (*Trigger): starttrigger of the act

            stoptrigger (*Trigger): stoptrigger of the act (optional)

            maneuvergroup (list of ManeuverGroup): list of ManeuverGroups belonging to the act

        Methods
        -------
            add_maneuver_group(maneuvergroup)
                adds a maneuvuergroup to the act

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,starttrigger=None,stoptrigger=None):
        """ Initalize the Act

            Parameters
            ----------
                name (str): name of the act

                starttrigger (*Trigger): starttrigger of the act
                    Default: ValueTrigger('act_start',0,ConditionEdge.none,SimulationTimeCondition(0,Rule.greaterThan))

                stoptrigger (*Trigger): stoptrigger of the act (optional)
                    Default: Emptytrigger

        """

        self.name = name
        if starttrigger == None:
            self.starttrigger = starttrigger = ValueTrigger('act_start',0,ConditionEdge.none,SimulationTimeCondition(0,Rule.greaterThan))
        elif starttrigger._triggerpoint == 'StopTrigger':
            raise ValueError('the starttrigger provided does not have start as the triggeringpoint')
        else:
            self.starttrigger = starttrigger

        if stoptrigger == None:
            self.stoptrigger = EmptyTrigger('stop')
        elif stoptrigger._triggerpoint == 'StartTrigger':
            raise ValueError('the stoptrigger provided is not of type StopTrigger')
        else:
            self.stoptrigger = stoptrigger

        self.maneuvergroup = []

    def add_maneuver_group(self,maneuvergroup):
        """ adds a maneuvuergroup to the act

            Parameters
            ----------
                maneuvergroup (ManeuverGroup): the maneuvergroup to add

        """
        if not isinstance(maneuvergroup,ManeuverGroup):
            raise TypeError('maneuvergroup is not of type ManeuverGroup')
        self.maneuvergroup.append(maneuvergroup)

    def get_attributes(self):
        """ returns the attributes as a dict of the Act

        """
        return {'name':self.name}

    def get_element(self):
        """ returns the elementTree of the Act

        """
        element = ET.Element('Act',attrib=self.get_attributes())
        if not self.maneuvergroup:
            raise ValueError('no maneuver group added to the act')
        for mangr in self.maneuvergroup:
            element.append(mangr.get_element())

        element.append(self.starttrigger.get_element())
        element.append(self.stoptrigger.get_element())
        return element

class ManeuverGroup():
    """ the ManeuverGroup creates the ManeuverGroup of the OpenScenario
        
        Parameters
        ----------
            name (str): name of the ManeuverGroup

            maxexecution (int): maximum number of iterations

            selecttriggeringentities (bool): Have no idea what this does ??? TODO: check

        Attributes
        ----------
            name (str): name of the ManeuverGroup

            maxexecution (int): maximum number of iterations

            selecttriggeringentities (bool): Have no idea what this does ??? TODO: check

            maneuvers (list of Maneuver): the maneuvers in the ManeuverGroup

            actors (_Actors): all actors of the ManeuverGroup

        Methods
        -------
            add_maneuver(Maneuver)
                adds a maneuver to the ManeuverGroup

            add_actor(entity)
                adds an actor to the ManeuverGroup

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,maxexecution=1,selecttriggeringentities = False):
        """ initalize the ManeuverGroup

            Parameters
            ----------
                name (str): name of the ManeuverGroup

                maxexecution (int): maximum number of iterations

                selecttriggeringentities (bool): Have no idea what this does ??? TODO: check
        
        """
        self.name = name
        self.maxexecution = maxexecution
        self.actors = _Actors(selecttriggeringentities)
        self.maneuvers = []
     
    def add_maneuver(self,maneuver):
        """ adds a maneuver to the ManeuverGroup
            
        Parameters
        ----------
            maneuver (Maneuver, or CatalogReference): maneuver to add

        """
        if not isinstance(maneuver,Maneuver):
            raise TypeError('maneuver input is not of type Maneuver')
        self.maneuvers.append(maneuver)

    def add_actor(self,entity):
        """ adds an actor to the ManeuverGroup
            
        Parameters
        ----------
            entity (str): name of the entity to add as an actor

        """
        self.actors.add_actor(entity)

    def get_attributes(self):
        """ returns the attributes as a dict of the ManeuverGroup

        """
        return {'name':self.name,'maximumExecutionCount':str(self.maxexecution)}

    def get_element(self):
        """ returns the elementTree of the ManeuverGroup

        """
        element = ET.Element('ManeuverGroup',attrib=self.get_attributes())
        element.append(self.actors.get_element())
        for man in self.maneuvers:
            element.append(man.get_element())
        return element



class _Actors():
    """ _Actors is used to create the actors of a ManeuverGroup
        
        Parameters
        ----------
            selectTriggeringEntities (bool): ???
                Default: False

        Attributes
        ----------
            selectTriggeringEntities (bool): ???

            actors (list or EntityRef): all actors to add to the element

        Methods
        -------
            add_actor(actor)
                adds an actor 

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self, selectTriggeringEntities=False):
        """ initalize the _Actors

            Parameters
            ----------
                selectTriggeringEntities (bool): ???
                    Default: False

        """
        self.actors = []
        self.select = selectTriggeringEntities

    

    def add_actor(self,entity):
        """ adds an actor to the list of actors
            
            Parameters
            ----------
                entity (str): name of the entity

        """
        self.actors.append(EntityRef(entity))

    def get_attributes(self):
        """ returns the attributes of the _Actors as a dict

        """
        return {'selectTriggeringEntities':convert_bool(self.select)}

    def get_element(self):
        """ returns the elementTree of the _Actors

        """
        # if not self.actors:
        #     raise ValueError('no actors are set')
        if len(self.actors) == 0:
            Warning('No Actors are defined')
        element = ET.Element('Actors',attrib=self.get_attributes())
        for ent in self.actors:
            element.append(ent.get_element())
        return element



class Maneuver():
    """ The Maneuver class creates the Maneuver of OpenScenario
        
        Parameters
        ----------
            name (str): name of the Maneuver

            parameters (ParameterDeclaration): Parameter declarations for the maneuver
                Default: None

        Attributes
        ----------
            name (str): name of the Maneuver

            events (list of Event): all events belonging to the Maneuver

            parameters (ParameterDeclaration): Parameter declarations for the maneuver

        Methods
        -------
            add_event (event)
                adds an event to the Maneuver

            append_to_catalog(filename)
                adds the vehicle to an existing catalog

            dump_to_catalog(filename,name,description,author)
                crates a new catalog with the vehicle

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,parameters = None):
        """ initalizes the Maneuver
        Parameters
        ----------
            name (str): name of the Maneuver

        """
        if parameters is not None and not isinstance(parameters,ParameterDeclarations):
            raise TypeError('parameters is not of type ParameterDeclarations')
        self.parameters = parameters
        self.name = name
        self.events = []

    def dump_to_catalog(self,filename,catalogtype,description,author):
        """ dump_to_catalog creates a new catalog and adds the Controller to it
            
            Parameters
            ----------
                filename (str): path of the new catalog file

                catalogtype (str): name of the catalog

                description (str): description of the catalog

                author (str): author of the catalog
        
        """
        cf = CatalogFile()
        cf.create_catalog(filename,catalogtype,description,author)
        cf.add_to_catalog(self)
        cf.dump()
        
    def append_to_catalog(self,filename):
        """ adds the Controller to an existing catalog

            Parameters
            ----------
                filename (str): path to the catalog file

        """
        cf = CatalogFile()
        cf.open_catalog(filename)
        cf.add_to_catalog(self)
        cf.dump()

    def add_event(self,event):
        """ adds an event to the Maneuver

        Parameters
        ----------
            name (Event): the event to add to the Maneuver

        """
        if not isinstance(event,Event):
            raise TypeError('event input is not of type Event')
        self.events.append(event)

    def get_attributes(self):
        """ returns the attributes as a dict of the Maneuver

        """
        return {'name':self.name}

    def get_element(self):
        """ returns the elementTree of the Maneuver

        """
        if not self.events:
            raise ValueError('no events added to the maneuver')

        element = ET.Element('Maneuver',attrib=self.get_attributes())
        if self.parameters:
            element.append(self.parameters.get_element())
        for event in self.events:
            element.append(event.get_element())

        return element

class Event():
    """ the Event class creates the event of OpenScenario
        
        Parameters
        ----------
            name (str): name of the event

            priority (Priority): what priority the event has 

            maxexecution (int): the maximum allowed executions of the event
                Default: 1

        Attributes
        ----------
            name (str): name of the event

            priority (Priority): what priority the event has TODO: add definition

            maxexecution (int): the maximum allowed executions of the event
                
            action (list of actions): all actions belonging to the event

            trigger (*Trigger): a start trigger to the event

        Methods
        -------
            add_trigger()
                adds an trigger to the event

            add_action()
                adds an action to the event (can be called multiple times)

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,priority,maxexecution=1):
        self.name = name
        if priority not in Priority:
            ValueError('Not a valid priority')
        self.priority = priority
        self.action = []
        self.trigger = None
        self.maxexecution = maxexecution

    def add_trigger(self,trigger):
        """ adds a starging trigger to the event

        Parameters
        ----------
            trigger (*Trigger): Adds a trigger to start the event (not EmptyTrigger)

        """
        if not isinstance(trigger,_TriggerType):
            if isinstance(trigger,_ValueTriggerType):
                raise TypeError('trigger input is a value trigger condition, please add to a ValueTrigger.')
            elif isinstance(_EntityTriggerType):
                raise TypeError('trigger input is a entity trigger condition, please add to a EntityTrigger.')
            raise TypeError('trigger input is not a valid trigger')
        self.trigger = trigger

    def add_action(self,actionname,action):
        """ adds an action to the Event, multiple actions can be added and will be ordered as added.

            Parameters
            ----------
                action (*Action): any action to be added to the event

        """
        if not isinstance(action,_ActionType):
            raise TypeError('action input is not a valid Action')
        self.action.append(_Action(actionname,action))

    def get_attributes(self):
        """ returns the attributes as a dict of the Event

        """
        return {'name':self.name,'priority':self.priority.name,'maximumExecutionCount':str(self.maxexecution)}

    def get_element(self):
        """ returns the elementTree of the Event

        """
        if not self.action:
            raise ValueError('no action(s) set')
        if not self.trigger:
            raise ValueError('no trigger set')

        element = ET.Element('Event',attrib=self.get_attributes())
        for action in self.action:
            element.append(action.get_element())

        element.append(self.trigger.get_element())
        return element
