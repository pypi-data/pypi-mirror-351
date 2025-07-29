from enum import Enum

# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_Direction(Enum):
    LeftAligned = 1
    CenterAligned = 2
    RightAligned = 3

# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_Owner(Enum):
    BlockConnector = 1
    BlockDevice = 2
    BlockPin = 3
    Bundle = 4
    Cable = 5
    CableCore = 6
    CableCoreEnd = 7
    CableEnd = 8
    CableType = 9
    CableTypeEnd = 10
    Component = 11
    ComponentPin = 12
    Connector = 13
    ConnectorPin = 14
    CoreType = 15
    CoreTypeEnd = 16
    DatabaseSymbol = 17
    Device = 18
    DevicePin = 19
    Dimension = 20
    FieldSymbol = 21
    FunctionalPort = 22
    FunctionalUnit = 23
    Graphic = 24
    Group = 25
    HoseTube = 26
    HoseTubeEnd = 27
    HoseTubeInside = 28 
    HoseTubeInsideEnd = 29
    HoseTubeInsideType = 30
    HoseTubeInsideTypeEnd = 31
    HoseTubeType = 32
    HoseTubeTypeEnd = 33
    Model = 34
    Module = 35
    Net = 36
    NetNode = 37
    NetSegment = 38
    Project = 39
    Sheet = 40
    SheetDatabase = 41
    Signal = 42
    SignalClass = 43
    SignalNode = 44
    Symbol = 45
    Text = 46
    VariantOptions = 47
    BusbarType = 48
    Busbar = 49


# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_Ratio(Enum):
    Normal = 1
    Narrow = 2
    Wide = 3

# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_Type(Enum):
    Integer = 1
    Real = 2
    LinearMeasure = 3
    String = 4
    Boolean = 5

# Used by
#	AttributeDefinitionInterface.Get
#	AttributeDefinitionInterface.Set
#	AttributeDefinitionInterface.Create
#	AttributeDefinitionInterface.GetFromDatabase
class AD_UniqueValue(Enum):
	NotUnique = 0
	Object = 1
	Project = 2
	Assignment = 3
	Location = 4
	AssignmentAndLocation = 5

# Used by
#	JobInterface::GetItemType
class ItemType(Enum):
	Undefined = 0
	Project = 1
	Component = 2
	ComponentPin = 4
	SymbolType = 5
	Device = 10
	Gate = 11
	DevicePin = 12
	Block = 13
	BlockConnector = 14
	BlockkConnectorPinGroup = 15
	BlockConnectorPin = 16
	Connector = 17
	ConnectorPinGroup = 18
	ConnectorPin = 19
	Cable = 20
	WireOrConductor = 22
	SignalOrSignalClass = 24
	Supply = 25
	AttributeDefinition = 26
	Attribute = 27
	Sheet = 28
	SheetReference = 29
	PlacedSymbolOrField = 30
	Text = 31
	ConnectLine = 32
	Node = 33
	Graphic = 34
	MenuItem35 = 35
	ProjectTreeOrMenuItem = 36
	MenuItem37 = 37
	Net = 38
	NetSegment = 39
	HierarchicalBlockOrModule = 46
	HierarchicalPort = 47
	Bundle = 50
	CableType = 51
	WireType = 52
	Slot = 59
	Contour = 60
	Position = 61
	MenuItem66 = 66
	MenuItem69 = 69
	MenuItem71 = 71
	FunctionalUnit = 72
	FunctionalPort = 73
	Group = 110
	MenuItem125 = 125
	Connection = 141
	ExternalDocument = 142
	MenuItem143 = 143
	Dimension = 151
	OptionOrVariant = 154
	PanelConnection = 156
	TestPoint = 163
	ClipboardOrStructureNode = 180
	MenuItem195 = 195
	MenuItem196 = 196
	StateItem = 200
	WireDifferenceItem = 201
	WireInformation = 202
	CavityPart = 208
	EmbeddedObject = 12292

# Used by
#   ApplictionInterface::GetModelList
class ModelType(Enum):
    Device = 1
    MountingRail = 2
    Busbar = 3
    CableDuct = 4
    PunchingStripCableDuct = 5
    CacleDuctInletOutlet = 6
    WireCombCableDuct = 7

# Used by
#   ApplictionInterface::GetProjectInformation
#   DbeApplictionInterface::GetProjectInformation
class ProjectType(Enum):
    Unsaved=0
    CableOrSchema = 1
    Logic = 2
    WireWorks = 3
    Demonstration = 4
    Student = 5

# Used by
#   SheetInterface::GetSchematicTypes
#   SheetInterface::SetSchematicTypes
class SchematicType(Enum):
    Electric = 0
    Hydraulic = 1
    Pneumatic = 2
    Process = 3
    Tubes = 4
    SingleLine = 5
    PanelSymbol = 6
 


