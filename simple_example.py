import pyoscx   






route = pyoscx.Route('myroute')

route.add_waypoint(pyoscx.WorldPosition(0,0,0,0,0,0),'closest')
route.add_waypoint(pyoscx.WorldPosition(1,1,0,0,0,0),'closest')

# pyoscx.prettyprint(route.get_element())



overrideaction = pyoscx.OverrideBrakeAction(0.3,True)
pyoscx.prettyprint(overrideaction.get_element())



catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','Catalogs/VehicleCatalogs')
catalog.add_catalog('ControllerCatalog','Catalogs/ControllerCatalogs')

roadfile = 'Databases/SampleDatabase.xodr'
road = pyoscx.RoadNetwork(roadfile)
# pyoscx.prettyprint(road.get_element())

trigcond = pyoscx.TimeToCollisionCondition(10,'equalTo',True,freespace=False,position=pyoscx.WorldPosition())

trigger = pyoscx.EntityTrigger('mytesttrigger',0.2,'rising',trigcond,'Target_1')

event = pyoscx.Event('myfirstevent','overwrite')
event.add_trigger(trigger)

TD = pyoscx.TransitionDynamics('step','rate',1)

lanechangeaction = pyoscx.AbsoluteLaneChangeAction(1,TD)
# pyoscx.prettyprint(lanechangeaction.get_element())

speedaction = pyoscx.AbsoluteSpeedAction(50,TD)
event.add_action('newspeed',speedaction)

man = pyoscx.Maneuver('my maneuver')
man.add_event(event)

mangr = pyoscx.ManeuverGroup('mangroup')
mangr.add_actor('Ego')
mangr.add_maneuver(man)

act = pyoscx.Act('my act',trigger)
act.add_maneuver_group(mangr)

story = pyoscx.Story('mystory')
story.add_act(act)


bb = pyoscx.BoundingBox(2,5,1.5,1.5,0,0.2)
fa = pyoscx.Axel(2,2,2,1,1)
ba = pyoscx.Axel(1,1,2,1,1)
veh = pyoscx.Vehicle('mycar','vehicle',bb,fa,ba,150,10,10)

veh.add_property_file('propfile.xml')
veh.add_property('myprop','12')


entities = pyoscx.Entities()
entities.add_scenario_object('Ego',veh)
entities.add_scenario_object('Target_1',veh)
entities.add_entity_bytype('Target_2','vehicle')
entities.add_entity_byref('Target_3','something')
init = pyoscx.Init()
egospeed = pyoscx.AbsoluteSpeedAction(10,TD)


init.add_init_action('Ego',egospeed)
init.add_init_action('Ego',pyoscx.TeleportAction(pyoscx.WorldPosition(1,2,3,0,0,0)))
init.add_init_action('Target_1',egospeed)
init.add_init_action('Target_1',pyoscx.TeleportAction(pyoscx.WorldPosition(1,5,3,0,0,0)))

sb = pyoscx.StoryBoard(init)
sb.add_story(story)

sce = pyoscx.Scenario('myscenario','Mandolin',pyoscx.ParameterDeclarations(),entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
# pyoscx.prettyprint(sce.get_element())
# sce.write_xml('myfirstscenario.xml',True)