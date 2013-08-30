if(!app){
	var app = new Ing();
}
app.data.filetypes = {
	'10': 'text',
	'20': 'image',
	'30': 'music',
	'40': 'video',
	'50': 'doc',
	'60': 'ppt',
	'70': 'scorm',
	'80': 'pdf',
    '90': 'html'
}
app.data.fileicons = {
	'10': 'fileTypeText',
	'20': 'fileTypeImg',
	'30': 'fileTypeAudio',
	'40': 'fileTypeVideo',
	'50': 'fileTypeText',
	'60': 'fileTypeSlide',
	'70': 'fileTypeScorm',
	'80': 'fileTypeText',
    '90': 'fileTypeText'
}
app.data.states = {
    'DRAFT'             : 'inuse',
    'ACTIVE'            : 'active',
    'ACTIVE - Assign'   : 'active',
    'ACTIVE - In use'   : 'active',
    'DEACTIVATED'       : 'inactive',
    'DEACTIVATED - Used': 'incative',
    'Removed'           : 'inactive',
    
    // -- redundant numeric codes in case we change status codes to numeric
    '1' : 'inuse',
    '2' : 'active',
    '3' : 'active',
    '4' : 'active',
    '5' : 'inactive',
    '6' : 'inactive',
    '7' : 'inactive'  
}
