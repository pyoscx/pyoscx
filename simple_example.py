import pyoscx   
    
catalog = pyoscx.Catalog()
catalog.add_catalog('VehicleCatalog','Catalogs/VehicleCatalogs')
catalog.add_catalog('ControllerCatalog','Catalogs/ControllerCatalogs')

roadfile = 'Databases/SampleDatabase.xodr'
road = pyoscx.RoadNetwork(roadfile)

trigcond = pyoscx.TimeToCollisionCondition(10,'equalTo',True,freespace=False,position=pyoscx.WorldPosition())

trigger = pyoscx.EntityTrigger('mytesttrigger',0.2,'rising',trigcond,'Target_1')

event = pyoscx.Event('myfirstevent','overwrite')
event.add_trigger(trigger)

TD = pyoscx.TransitionDynamics('step',0,'rate',1)

speedaction = pyoscx.SpeedAction(TD)
speedaction.set_absolute_target_speed(50)
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

ego = pyoscx.ScenarioObject('Ego')
ego.set_catalog_reference('VehicleCatalog','S90')
ego.set_object_controller('ControllerCatalog','Default')

tar = pyoscx.ScenarioObject('Target_1')
tar.set_catalog_reference('VehicleCatalog','A3')
tar.set_object_controller('ControllerCatalog','Default')

entities = pyoscx.Entities()
entities.add_scenario_object(ego)
entities.add_scenario_object(tar)

init = pyoscx.Init()
egospeed = pyoscx.SpeedAction(TD)
egospeed.set_absolute_target_speed(10)

init.add_init_action('Ego',egospeed)
init.add_init_action('Ego',pyoscx.TeleportAction(pyoscx.WorldPosition(1,2,3,0,0,0)))
init.add_init_action('Target_1',egospeed)
init.add_init_action('Target_1',pyoscx.TeleportAction(pyoscx.WorldPosition(1,5,3,0,0,0)))

sb = pyoscx.StoryBoard(init)
sb.add_story(story)

sce = pyoscx.Scenario('myscenario','Mandolin',pyoscx.ParameterDeclarations(),entities=entities,storyboard = sb,roadnetwork=road,catalog=catalog)
# pyoscx.prettyprint(sce.get_element())
sce.write_xml('myfirstscenario.xml',True)