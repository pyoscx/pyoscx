import pyoscx   






### create catalogs
catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','../xosc/Catalogs/Vehicles')



### create road
road = pyoscx.RoadNetwork(roadfile='../xodr/e6mini.xodr',scenegraph='../models/e6mini.osgb')


### create parameters
paramdec = pyoscx.ParameterDeclarations()

paramdec.add_parameter(pyoscx.Parameter('$HostVehicle','string','car_white'))
paramdec.add_parameter(pyoscx.Parameter('$TargetVehicle','string','car_red'))

### create vehicles

bb = pyoscx.BoundingBox(2,5,1.8,2.0,0,0.9)
fa = pyoscx.Axel(30,0.8,1.68,2.98,0.4)
ba = pyoscx.Axel(30,0.8,1.68,0,0.4)
white_veh = pyoscx.Vehicle('car_white','car',bb,fa,ba,69,10,10)

white_veh.add_property_file('../models/car_white.osgb')
white_veh.add_property('control','internal')
white_veh.add_property('model_id','0')


bb = pyoscx.BoundingBox(1.8,4.5,1.5,1.3,0,0.8)
fa = pyoscx.Axel(30,0.8,1.68,2.98,0.4)
ba = pyoscx.Axel(30,0.8,1.68,0,0.4)
red_veh = pyoscx.Vehicle('car_red','car',bb,fa,ba,69,10,10)

red_veh.add_property_file('../models/car_red.osgb')
red_veh.add_property('model_id','2')

## create entities

egoname = 'Ego'
targetname = 'Target'

entities = pyoscx.Entities()
entities.add_scenario_object(egoname,white_veh)
entities.add_scenario_object(targetname,red_veh)


### create init

init = pyoscx.Init()
step_time = pyoscx.TransitionDynamics('step','time',1)

egospeed = pyoscx.AbsoluteSpeedAction(30,step_time)
egostart = pyoscx.TeleportAction(pyoscx.LanePosition(25,0,-3,0))

targetspeed = pyoscx.AbsoluteSpeedAction(40,step_time)
targetstart = pyoscx.TeleportAction(pyoscx.LanePosition(15,0,-2,0))

init.add_init_action(egoname,egospeed)
init.add_init_action(egoname,egostart)
init.add_init_action(targetname,targetspeed)
init.add_init_action(targetname,targetstart)


### create an event

trigcond = pyoscx.TimeHeadwayCondition(targetname,0.1,'greaterThan')

trigger = pyoscx.EntityTrigger('mytesttrigger',0.2,'rising',trigcond,egoname)

event = pyoscx.Event('myfirstevent','overwrite')
event.add_trigger(trigger)

sin_time = pyoscx.TransitionDynamics('linear','time',3)
# action = pyoscx.AbsoluteSpeedAction(30,sin_time)
action = pyoscx.LongitudinalDistanceAction(-4,egoname,max_deceleration=3,max_speed=50)
# action = pyoscx.LongitudinalTimegapAction(-0.2,egoname,max_deceleration=3)
# action = pyoscx.actions.RelativeLaneOffsetAction(-1,egoname,'linear',1)
# action = pyoscx.actions.AbsoluteLaneOffsetAction(2,'linear',1)
# action = pyoscx.actions.AbsoluteLaneChangeAction(-4,sin_time)
# action = pyoscx.actions.RelativeLaneChangeAction(-2,egoname,sin_time)
event.add_action('newspeed',action)


## create maneuver and stuff
man = pyoscx.Maneuver('my_maneuver')
man.add_event(event)

mangr = pyoscx.ManeuverGroup('mangroup')
mangr.add_actor('$owner')
mangr.add_maneuver(man)
starttrigger = pyoscx.ValueTrigger('starttrigger',0,'rising',pyoscx.SimulationTimeCondition(0,'greaterThan'))
act = pyoscx.Act('my_act',starttrigger)
act.add_maneuver_group(mangr)

storyparam = pyoscx.ParameterDeclarations()
storyparam.add_parameter(pyoscx.Parameter('$owner','string',targetname))
story = pyoscx.Story('mystory',storyparam)
story.add_act(act)


sb = pyoscx.StoryBoard(init)
sb.add_story(story)


sce = pyoscx.Scenario('myscenario','Mandolin',paramdec,entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
# pyoscx.prettyprint(sce.get_element())
# sce.write_xml('myfirstscenario.xml',True)

pyoscx.esminiRunner(sce)