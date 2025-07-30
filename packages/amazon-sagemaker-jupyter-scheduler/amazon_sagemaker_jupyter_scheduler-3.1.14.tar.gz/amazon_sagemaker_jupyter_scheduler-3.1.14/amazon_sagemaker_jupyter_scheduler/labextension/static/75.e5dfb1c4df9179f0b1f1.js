"use strict";(self.webpackChunk_amzn_sagemaker_jupyter_scheduler=self.webpackChunk_amzn_sagemaker_jupyter_scheduler||[]).push([[75],{2372:(e,t,r)=>{r.r(t),r.d(t,{default:()=>zt});var n=r(6271),o=r.n(n),a=r(7363),i=r(3422);const l={ScheduleNoteBook:{MainPanel:{AdvancedOptions:{options:"Advanced Options",environmentVariables:"Environment variables",addEnvironmentvariable:"Add Variable",Key:"Key",Value:"Value",RoleArn:"Role ARN",Image:"Image",Kernel:"Kernel",securityGroup:"Security Group(s)",subnet:"Subnet(s)",s3InputFolder:"Input Folder",inputInDifferentAccount:"Input bucket is not in current account",inputInDifferentAccountLabel:"Enter input account ID",s3OutputFolder:"Output Folder",outputInDifferentAccount:"Output bucket is not in current account",outputInDifferentAccountLabel:"Enter output account ID",maxRetryAttempts:"Max retry attempts",maxRunTimeInSeconds:"Max run time (in seconds)",selectAdditionalDepency:"Select additional dependencies",efsPlaceholder:"Enter EFS file path",efsLabel:"Initialization script location (optional)",startUpScript:"Start-up script",executionEnv:"Execution enviroment",useVPC:"Use a Virtual Private Cloud (VPC) to run this job",enableNetworkIsolation:"Enable Network Isolation",enableEncryption:"Configure job encryption",enterKMSArnOrID:"Enter KMS key ID or ARN",ebsKey:"Job instance volume encryption KMS key",kmsKey:"Output encryption KMS key",Placeholders:{selectOrAdd:"select or add",No:"No",Add:"Add",NoneSelected:"None selected",SelectPrivateSubnets:"Select private subnet(s)",NoPrivateSubnets:"No private subnet(s) available",ImagePlaceHolder:"accountId.dkr.ecr.Region.amazonaws.com/repository[:tag] or [@digest]",KernelPlaceHolder:"kernel name",RolePlaceHolder:"arn:aws:iam::YourAccountID:role/YourRole",S3BucketPlaceHolder:"s3://bucket/path-to-your-data/"}},ErrorMessages:{JobEnvironment:{KernelImageExistError:"Image must be selected"},AdvancedOptions:{ImageError:"Image cannot be empty.",KernelError:"Kernel cannot be empty.",EFSFilePathError:"File path is not valid.",RoleArnLengthError:"Role ARN must have minimum length of 20 and maximum length of 2048.",RoleArnFormatError:"Role ARN is not properly formatted.",S3LengthError:"S3 Path must contain characters.",S3FormatError:"Invalid S3 Path format.",SecurityGroupMinError:"At least one Security Group must be selected when Subnet is selected.",SecurityGroupsMaxError:"Can only have a maximum of 5 Security Groups.",SecurityGroupSGError:"Security Group must start with sg-.",SecurityGroupLengthError:"Security Group must be less than 32 characters.",SecurityGroupFormatError:"Security Group has invalid format.",SubnetMinError:"At least one Subnet must be selected when Security Group is selected.",SubnetsMaxError:"Can only have maximum of 16 subnets.",SubnetLengthError:"Subnet must be less than 32 characters.",SubnetsFormatError:"One or more subnets has invalid format.",EnvironmentVariableEmptyError:"Key or Value cannot be empty.",EnvironmentVariableLengthError:"Key or Value cannot be more than 512 characters.",EnvironmentVariableFormatError:"Key or Value has invalid format.",KMSKeyError:"KMS key has invalid format.",MaxRetryAttemptsError:"Invalid max retry attempts must have a minimum value of 1 and a maximum value of 30.",MaxRunTimeInSecondsError:"Invalid max run time must have a minimum value of 1."},VPCErrors:{RequiresPrivateSubnet:"Running notebook jobs in a VPC requires the virtual network to use a private subnet.",NoPrivateSubnetsInSageMakerDomain:"There are no private subnets associated with your SageMaker Studio domain",YouMayChooseOtherSubnets:"You may choose to run the job using other private subnets associated with this VPC"}},Tooltips:{ImageTooltipText:"Enter the ECR registry path of the Docker image that contains the required Kernel & Libraries to execute the notebook. sagemaker-base-python-38 is selected by default",KernelTooltipText:"Enter the display name of kernel to execute the given notebook. This kernel should be installed in the above image.",LCCScriptTooltipText:"Select a lifecycle configuration script that will be run on image start-up.",VPCTooltip:"Configure the virtual network to run this job in a Virtual Private Cloud (VPC).",KMSTooltip:"Configure the cryptographic keys used to encrypt files in the job.",RoleArnTooltip:"Enter the IAM Role ARN with appropriate permissions needed to execute the notebook. By default Role name with prefix SagemakerJupyterScheduler is selected",SecurityGroupsTooltip:"Specify or add security group(s) of the desired VPC.",SubnetTooltip:"Specify or add Private subnet(s) of the desired VPC.",InputFolderTooltip:"Enter the S3 location to store the input artifacts like notebook and script.",OutputFolderTooltip:"Enter the S3 location to store the output artifacts.",InitialScriptTooltip:"Enter the file path of a local script to run before the notebook execution.",EnvironmentVariablesTooltip:"Enter key-value pairs that will be accessible in your notebook.",networkIsolationTooltip:"Enable network isolation.",kmsKeyTooltip:"If you want Amazon SageMaker to encrypt the output of your notebook job using your own AWS KMS encryption key instead of the default S3 service key, provide its ID or ARN",ebsKeyTooltip:"Encrypt data on the storage volume attached to the compute instance that runs the scheduled job.",LearnMore:"Learn more",MaxRetryAttempts:"Enter a minimum value of 1 and a maximum value of 30.",MaxRunTimeInSeconds:"Enter a minimum value of 1."},StudioTooltips:{ImageTooltipText:"Select available SageMaker image.",KernelTooltipText:"Select available SageMaker Kernel.",RoleArnTooltip:"Specify a role with permission to create a notebook job.",SecurityGroupsTooltip:"Specify or add security group(s) that have been created for the default VPC. For better security, we recommend that you use a private VPC.",SubnetTooltip:"Specify or add subnet(s) that have been created for the default VPC. For better security, we recommend that you use a private VPC.",InputFolderTooltip:"Enter the S3 location where the input folder it is located.",InputAccountIdTooltip:"Enter the S3 location where the input folder it is located.",OutputFolderTooltip:"Enter the S3 location where the output folder it is located.",OutputAccountIdTooltip:"Enter the S3 location where the input folder it is located.",InitialScriptTooltip:"Enter the EFS file path where a local script or a lifecycle configuration script is located."}}},ImageSelector:{label:"Image"},KernelSelector:{label:"Kernel",imageSelectorOption:{linkText:"More Info"}},Dialog:{awsCredentialsError:{title:"You’re not authenticated to your AWS account.",body:{text:["You haven’t provided AWS security keys or they expired. Authenticate to your AWS account with valid security keys before creating a notebook job.","Note that you must have an AWS account configured with a proper role to create notebook jobs. See %{schedulerInformation} for instructions."],links:{schedulerInformation:{linkString:"Notebook Scheduler information",linkHref:"https://docs.aws.amazon.com/sagemaker/latest/dg/notebook-auto-run.html"}}},buttons:{goToIamConsole:"Go to IAM console",enterKeysInTerminal:"Run `aws configure` in Terminal"}}}},s={expiredToken:"ExpiredToken",invalidClientTokenId:"InvalidClientTokenId",noCredentials:"NoCredentials"},u="terminal:create-new";var c,d=r(5185),m=r(3626),p=r(6516),v=r(1396),b=r(6247);!function(e){e.PublicInternetOnly="PublicInternetOnly",e.VpcOnly="VpcOnly"}(c||(c={}));var g,h,f=r(9849),E=r(9208),y=r(1982);!function(e){e[e.Large=0]="Large",e[e.Medium=1]="Medium",e[e.Small=2]="Small"}(g||(g={})),function(e){e.Filled="filled"}(h||(h={}));const _={[g.Large]:"var(--jp-content-line-height-3)",[g.Medium]:"var(--jp-content-line-height-2)",[g.Small]:"var(--jp-content-line-height-1-25)"},S={[g.Large]:"1em",[g.Medium]:"0.5em",[g.Small]:"0.25em"},k=e=>y.css`
  root: {
    background: 'var(--jp-input-active-background)',
    borderTopLeftRadius: 'var(--jp-border-radius)',
    borderTopRightRadius: 'var(--jp-border-radius)',
    fontSize: 'var(--jp-ui-font-size2)',
    '&.Mui-focused': {
      background: 'var(--jp-input-active-background)',
    },
    '&.Mui-disabled': {
      borderRadius: 'var(--jp-border-radius)',
      color: 'var(--text-input-font-color-disabled)',
    },
    '&.MuiInput-underline.Mui-disabled:before': {
      borderBottom: 'none',
    },
  },
  underline: {
    borderBottom: 'none',
    '&:before': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&:not(.Mui-disabled):hover:before': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&.Mui-error:hover:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
    '&.Mui-error:after': {
      borderBottom: 'var(--jp-border-width) solid',
    },
  },
  input: {
    color: 'var(--jp-ui-font-color0)',
    lineHeight: ${_[e]},
    padding: ${S[e]},
  },   
`,j=(y.css`
  root: {
    fontFamily: 'var(--jp-cell-prompt-font-family)',
    color: 'var(--jp-input-border-color)',
    marginBottom: 'var(--padding-small)',
    '&.Mui-error': {
      fontFamily: 'var(--jp-cell-prompt-font-family)',
      color: 'var(--jp-error-color1)',
    },
    '&.Mui-disabled': {
      fontFamily: 'var(--jp-cell-prompt-font-family)',
      color: 'var(--jp-error-color1)',
    },
  },
`,({classes:e,className:t,InputProps:r,FormHelperTextProps:n,size:a=g.Medium,variant:i,...l})=>{var s,u,c;const d=(0,y.cx)(y.css`
  .MuiFormHelperText-root.Mui-error::before {
    display: inline-block;
    vertical-align: middle;
    background-size: 1rem 1rem;
    height: var(--text-input-error-icon-height);
    width: var(--text-input-error-icon-width);
    background-image: var(--text-input-helper-text-alert-icon);
    background-repeat: no-repeat;
    content: ' ';
  }
`,t,null==e?void 0:e.root);return o().createElement(f.TextField,{"data-testid":"inputField",classes:{root:d,...e},variant:i,role:"textField",InputProps:{...r,classes:{root:(0,y.cx)(k(a),null===(s=null==r?void 0:r.classes)||void 0===s?void 0:s.root),input:(0,y.cx)(k(a),null===(u=null==r?void 0:r.classes)||void 0===u?void 0:u.input)}},FormHelperTextProps:{...n,classes:{root:(0,y.cx)(y.css`
    fontSize: 'var(--jp-ui-font-size0)',
    color: 'var(--text-input-helper-text)',
    '&.Mui-error': {
      color: 'var(--jp-error-color1)',
    },
    '&.Mui-disabled': {
      color: 'var(--jp-error-color1)',
    },
`,null===(c=null==n?void 0:n.classes)||void 0===c?void 0:c.root)}},...l})});var x,w=r(4129);!function(e){e.TopStart="top-start",e.Top="top",e.TopEnd="top-end",e.RightStart="right-start",e.Right="right",e.RightEnd="right-end",e.BottomStart="bottom-start",e.Bottom="bottom",e.BottomEnd="bottom-end",e.LeftStart="left-start",e.Left="left",e.LeftEnd="left-end"}(x||(x={}));const C=({children:e,classes:t,className:r,placement:n=x.Right,...a})=>{const i=(0,y.cx)(r,y.css`
  popper: {
    '& .MuiTooltip-tooltip': {
      backgroundColor: 'var(--color-light)',
      boxShadow: 'var(--tooltip-shadow)',
      color: 'var(--tooltip-text-color',
      padding: 'var(--padding-16)',
      fontSize: 'var(--font-size-0)',
    },
  },
`,null==t?void 0:t.popper);return o().createElement(w.Z,{...a,arrow:!0,classes:{popper:i,tooltip:y.css`
  tooltip: {
    '& .MuiTooltip-arrow': {
      color: 'var(--tooltip-surface)',
      '&:before': {
        boxShadow: 'var(--tooltip-shadow)',
      },
    },
  },
`},placement:n,"data-testid":"toolTip"},e)},T=y.css`
  display: flex;
  flex-direction: column;
`,P=y.css`
  display: flex;
  flex-direction: column;
`,M=y.css`
  display: inline-flex;
  svg {
    width: 0.75em;
    height: 0.75em;
    transform: translateY(-2px);
  }
`,I=y.css`
  svg {
    width: 0.75em;
    height: 0.75em;
    transform: translateY(1px);
  }
`,N=(e=!1)=>y.css`
  display: flex;
  flex-direction: column;
  ${e?"":"max-width : 500px;"}
  .MuiCheckbox-colorPrimary.Mui-checked {
    color: var(--jp-brand-color1);
  }
  .MuiButton-containedPrimary:hover {
    background-color: var(--jp-brand-color1);
  }
`,O=y.css`
  font-size: var(--jp-content-font-size1);
`,F=y.css`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 0.5rem;
  svg {
    width: var(--jp-ui-font-size1);
    height: var(--jp-ui-font-size1);
    path {
      fill: var(--jp-error-color1);
    }
  }
`,J=(e=!1)=>y.css`
  color: var(--jp-color-root-light-800);
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
  margin-bottom: var(--jp-ui-font-size1);
  ${e&&"\n    &:after {\n      content: '*';\n      color: var(--jp-error-color1);\n    }\n  "}
`;var D,A;!function(e){e.External="_blank",e.Content="_self"}(D||(D={})),function(e){e.None="none",e.Hover="hover",e.Always="always"}(A||(A={}));const V=({className:e,disabled:t=!1,children:r,onClick:n,target:a=D.Content,...i})=>{const l=a===D.External,s={...i,className:(0,y.cx)(y.css`
  cursor: pointer;
  text-decoration: none;
  color: var(--jp-brand-color1);

  &:hover {
    text-decoration: none;
    color: var(--jp-brand-color1);
  }
`,e),target:a,onClick:t?void 0:n,rel:l?"noopener noreferrer":void 0};return o().createElement(f.Link,{...s,"data-testid":"link"},r)};r(78);const R=e=>"string"==typeof e&&e.length>0;var L=r(5505),$=r.n(L);function z(e){try{if(!$()(e)||0===e.length)return{kernel:null,arnEnvironment:null,version:null};const t=e.split("__SAGEMAKER_INTERNAL__"),[r,n]=t,o=n&&n.split("/"),a=o&&o[0]+"/"+o[1],i=3===o.length?o[2]:null;return{kernel:r,arnEnvironment:i?`${a}/${i}`:a,version:i}}catch(e){return{kernel:null,arnEnvironment:null,version:null}}}const K=({labelInfo:e,required:t,toolTipText:r,errorMessage:n,...a})=>o().createElement("div",{className:P},o().createElement("div",{className:M},o().createElement("label",{className:J(t)}," ",e," "),r&&!a.readOnly&&o().createElement(C,{title:r,className:I},o().createElement(E.Z,null))),o().createElement(j,{...a,error:R(n),helperText:n,InputProps:{readOnly:a.readOnly,...a.InputProps}}));var B=r(6433);y.css`
  box-sizing: border-box;
  width: 100%;
  padding: var(--jp-padding-large);
  flex-direction: column;
  display: flex;
  color: var(--jp-ui-font-color0);
`,y.css`
  width: 100%;
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  padding-bottom: var(--jp-padding-20);
  color: var(--jp-ui-font-color0);
`,y.css`
  max-width: 525px;
  color: var(--jp-ui-font-color2);
  margin-bottom: var(--jp-padding-medium);
`,y.css`
  display: block;
  margin-bottom: 0.5em;
  overflow-y: scroll;
`,y.css`
  align-items: center;
  display: inline-flex;
  margin-bottom: var(--jp-padding-16);
  margin-left: 1em;
  font-size: var(--jp-ui-font-size3);
  color: var(--jp-ui-font-color0);
`;const G=y.css`
  display: flex;
  flex-direction: column;
  font-size: 12px;
  color: var(--jp-ui-font-color0);
  padding: 10px;
  overflow-x: auto;
  overflow-y: hidden;
  gap: 20px;
`,q=(y.css`
  display: flex;
  justify-content: space-between;
`,y.css`
  display: flex;
  align-items: center;
`,y.css`
  margin-bottom: var(--jp-padding-medium);
`,y.css`
  width: 50% !important;
  text-align: center;
  height: 30px;
  font-size: 12px !important;
`,y.css`
  display: inline-flex;
  justify-content: right;
`,y.css`
  height: fit-content;
  width: 90px;
  text-align: center;
  margin-right: var(--jp-padding-medium);
`,y.css`
  position: absolute;
  right: 0%;
  bottom: 0%;
  margin-bottom: var(--jp-padding-large);
`,y.css`
  div:nth-child(2) {
    width: 98%;
  }
`,y.css`
  div:nth-child(2) {
    width: 49%;
  }
`,y.css`
  div:nth-child(2) {
    width: 150px;
  }
`,y.css`
  width: 500px;
  margin-bottom: var(--jp-size-4);
`),Z=y.css`
  display: flex;
  align-items: center;
`,H=y.css`
  display: flex;
  align-items: center;
`,U=y.css`
  color: var(--jp-brand-color3);
`,Y=y.css`
  padding: 4px;
`,W=y.css`
  color: var(--jp-ui-font-color0);
`,Q=y.css`
  display: flex;
  flex-direction: column;
  gap: var(--jp-ui-font-size1);
`,X=y.css`
  color: var(--jp-error-color1);
  padding: 12px;
`,ee=l.ScheduleNoteBook.MainPanel.ErrorMessages.VPCErrors,te=l.ScheduleNoteBook.MainPanel.AdvancedOptions,re=l.ScheduleNoteBook.MainPanel.Tooltips,ne=o().createElement("div",null,o().createElement("span",{className:H}," ",re.VPCTooltip," "),o().createElement(V,{href:"https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html",target:D.External},o().createElement("p",{className:U},l.ScheduleNoteBook.MainPanel.Tooltips.LearnMore))),oe=({isChecked:e,formState:t,formErrors:r,initialSecurityGroups:n,initialSubnets:a,availableSubnets:i,setFormErrors:l,setChecked:s,setFormState:u,...c})=>o().createElement("div",{className:Z},o().createElement(B.Z,{name:"vpc-check-box",className:Y,color:"primary",checked:e,onChange:e=>{const o=e.target.checked;if(s(o),o){if(u({...t,vpc_security_group_ids:n,vpc_subnets:a}),0===a.length&&i.length>0)return void l({...r,subnetError:`${ee.RequiresPrivateSubnet} ${ee.NoPrivateSubnetsInSageMakerDomain}. ${ee.YouMayChooseOtherSubnets}`});0===i.length&&l({...r,subnetError:`${ee.RequiresPrivateSubnet} ${ee.NoPrivateSubnetsInSageMakerDomain}`})}else u({...t,vpc_security_group_ids:[],vpc_subnets:[]}),l({...r,subnetError:"",securityGroupError:""})},...c}),o().createElement("label",null,te.useVPC),o().createElement(C,{classes:{popperInteractive:W},title:ne},o().createElement(E.Z,{fontSize:"small"})));var ae=r(9419),ie=r(2679),le=r(4085);const se=y.css`
  display: flex;
  align-items: flex-end;
  padding-right: 1em;
  gap: 20px;
`,ue=y.css`
  display: flex;
  flex-direction: column;
`,ce=y.css`
  width: 170px;
`,de=(y.css`
  display: flex;
  flex-direction: column;
  margin-bottom: var(--jp-padding-large);
`,y.css`
  display: flex;
  flex-direction: column;
  gap: 16px;
`),me=y.css`
  font-weight: 400;
  font-size: var(--jp-ui-font-size1);
  line-height: var(--jp-ui-font-size1);
`,pe=y.css`
  background-color: var(--jp-brand-color1);
  font-size: var(--jp-ui-font-size1);
  text-transform: none;
`,ve=y.css`
  display: inline-flex;
  align-items: center;
  gap: 6px;
  svg {
    width: 0.75em;
    height: 0.75em;
  }
`,be=new RegExp("[a-zA-Z_][a-zA-Z0-9_]*"),ge=new RegExp("[\\S\\s]*"),he=l.ScheduleNoteBook.MainPanel.ErrorMessages.AdvancedOptions,fe=l.ScheduleNoteBook.MainPanel.AdvancedOptions,Ee=({isDisabled:e,environmentParameters:t,setEnvironmentParameters:r,index:n,formErrors:a,setFormErrors:i})=>{const l=t[n],s=e=>{const n=e.currentTarget.name,o=e.target.value,[a,i]=n.split("-"),l="envKey"===a?{key:o,value:t[i].value}:{key:t[i].key,value:o},s=[...t];s.splice(i,1,l),r(s)},u=()=>{const{key:e,value:t}=l;e.length<1||t.length<1?i({...a,environmentVariablesError:he.EnvironmentVariableEmptyError}):e.length>512||t.length>512?i({...a,environmentVariablesError:he.EnvironmentVariableLengthError}):be.test(e)&&ge.test(t)?i({...a,environmentVariablesError:""}):i({...a,environmentVariablesError:he.EnvironmentVariableFormatError})};return o().createElement("div",{className:se},o().createElement(K,{className:ce,readOnly:e,name:`envKey-${n}`,labelInfo:fe.Key,value:t[n].key,onChange:s,onBlur:u}),o().createElement(K,{className:ce,readOnly:e,name:`envValue-${n}`,labelInfo:fe.Value,value:t[n].value,onChange:s,onBlur:u}),o().createElement("div",null,!e&&o().createElement(le.Z,{onClick:()=>{(e=>{const n=[...t];n.splice(e,1),r(n),i({...a,environmentVariablesError:""})})(n),i({...a,environmentVariablesError:""})},size:"large"},o().createElement(ie.Z,null))))},ye=l.ScheduleNoteBook.MainPanel.AdvancedOptions,_e=l.ScheduleNoteBook.MainPanel.Tooltips,Se=({allFieldsDisabled:e,isButtonDisabled:t,environmentVariables:r,setEnvironmentVariables:n,formErrors:a,...i})=>{const l=!!a.environmentVariablesError,s=o().createElement("div",{className:F},o().createElement(ae.Z,{severity:"error"},a.environmentVariablesError));return o().createElement("div",{className:de},o().createElement("div",{className:ve},o().createElement("label",{className:me},ye.environmentVariables),e?null:o().createElement(C,{title:_e.EnvironmentVariablesTooltip},o().createElement(E.Z,null))),e&&0===r.length?o().createElement("div",{className:ue},o().createElement(j,{InputProps:{readOnly:!0},placeholder:ye.Placeholders.NoneSelected})):o().createElement(o().Fragment,null,r.map(((t,l)=>o().createElement(Ee,{isDisabled:e,key:l,environmentParameters:r,setEnvironmentParameters:n,index:l,formErrors:a,...i})))),l&&o().createElement("div",null,s),!e&&o().createElement("div",null,o().createElement(f.Button,{disabled:t,className:pe,variant:"contained",color:"primary",size:"small",onClick:()=>{n([...r,{key:"",value:""}])}},ye.addEnvironmentvariable)))};var ke=r(8992),je=r(7338),xe=r(1360);const we=(0,ke.D)(),Ce=({label:e,required:t,errorMessage:r,disabled:n,renderInput:a,tooltip:i,disabledTooltip:l,freeSolo:s,options:u,...c})=>{var d,m;null!=a||(a=t=>o().createElement(xe.Z,{...t,variant:"outlined",size:"small",margin:"dense",placeholder:e}));const p=n?l?o().createElement(C,{title:l,className:I},o().createElement(E.Z,null)):o().createElement(o().Fragment,null):i?o().createElement(C,{title:i,className:I},o().createElement(E.Z,null)):o().createElement(o().Fragment,null),v=r?o().createElement("div",{className:F},o().createElement(ae.Z,{severity:"error"},r)):o().createElement(o().Fragment,null);return o().createElement("div",{className:T},o().createElement("div",{className:M},o().createElement("label",{className:J(t)},e),p),o().createElement(je.Z,{...c,multiple:!0,renderInput:a,freeSolo:s,readOnly:n,options:u,filterOptions:(e,t)=>{const r=we(e,t);return""===t.inputValue||e.includes(t.inputValue)||r.push(t.inputValue),r},renderOption:(e,t,r)=>(u.includes(t)||(t=`Add "${t}"`),o().createElement("li",{...e},t)),componentsProps:{...c.componentsProps,popupIndicator:{...null===(d=c.componentsProps)||void 0===d?void 0:d.popupIndicator,size:"small"},clearIndicator:{...null===(m=c.componentsProps)||void 0===m?void 0:m.clearIndicator,size:"small"}}}),v)},Te=new RegExp("^(https|s3)://([^/]+)/?(.*)$"),Pe=new RegExp("[-0-9a-zA-Z]+"),Me=new RegExp("^arn:aws[a-z\\-]*:iam::\\d{12}:role/?[a-zA-Z_0-9+=,.@\\-_/]+$"),Ie=new RegExp("^arn:aws:kms:\\w+(?:-\\w+)+:\\d{12}:key\\/[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+$"),Ne=new RegExp("^[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}$"),Oe=l.ScheduleNoteBook.MainPanel.ErrorMessages,Fe=Oe.VPCErrors,Je=e=>e.length<20||e.length>2048?Oe.AdvancedOptions.RoleArnLengthError:Me.test(e)?"":Oe.AdvancedOptions.RoleArnFormatError,De=e=>0===e.trim().length?Oe.AdvancedOptions.S3LengthError:Te.test(e)?"":Oe.AdvancedOptions.S3FormatError,Ae=e=>0===e.length||Ie.test(e)||Ne.test(e)?"":Oe.AdvancedOptions.KMSKeyError;var Ve;!function(e){e.LocalJL="local-jupyter-lab",e.JupyterLab="jupyterlab",e.Studio="studio"}(Ve||(Ve={}));class Re{get isStudio(){return this.type===Ve.Studio}get isLocalJL(){return this.type===Ve.LocalJL}get isJupyterLab(){return this.type===Ve.JupyterLab}get isStudioOrJupyterLab(){return this.isStudio||this.isJupyterLab}constructor(e){this.type=e}}const Le=(0,n.createContext)(void 0);function $e({app:e,children:t}){const[r,a]=(0,n.useState)((()=>function(e){return e.hasPlugin("@amzn/sagemaker-ui:project")?new Re(Ve.Studio):e.hasPlugin("@amzn/sagemaker-jupyterlab-extensions:sessionmanagement")?new Re(Ve.JupyterLab):new Re(Ve.LocalJL)}(e))),i={pluginEnvironment:r,setPluginEnvironment:a};return o().createElement(Le.Provider,{value:i},t)}function ze(){const e=(0,n.useContext)(Le);if(void 0===e)throw new Error("usePluginEnvironment must be used within a PluginEnvironmentProvider");return e}var Ke=r(2346),Be=r(3274),Ge=r(8102);const qe=l.ScheduleNoteBook.MainPanel.AdvancedOptions,Ze=l.ScheduleNoteBook.MainPanel.Tooltips,He=l.ScheduleNoteBook.MainPanel.StudioTooltips,Ue=l.ScheduleNoteBook.MainPanel.ErrorMessages,Ye=o().createElement("div",null,o().createElement("span",{className:H},Ze.networkIsolationTooltip),o().createElement(V,{href:"https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_CreateTrainingJob.html#sagemaker-CreateTrainingJob-request-EnableNetworkIsolation",target:D.External},o().createElement("p",{className:U},Ze.LearnMore))),We=o().createElement("div",null,o().createElement("span",{className:H},Ze.kmsKeyTooltip),o().createElement(V,{href:"https://docs.aws.amazon.com/sagemaker/latest/dg/create-notebook-auto-execution-advanced.html",target:D.External},o().createElement("p",{className:U},Ze.LearnMore))),Qe=o().createElement("div",null,o().createElement("span",{className:H},Ze.LCCScriptTooltipText),o().createElement(V,{href:"https://aws.amazon.com/blogs/machine-learning/customize-amazon-sagemaker-studio-using-lifecycle-configurations/",target:D.External},o().createElement("p",{className:U},Ze.LearnMore))),Xe=({isDisabled:e,formState:t,formErrors:r,environmentVariables:a,setEnvironmentVariables:i,lccOptions:l,availableSecurityGroups:s,availableSubnets:u,initialSubnets:c,initialSecurityGroups:d,isVPCDomain:m,requestClient:p,enableVPCSetting:g,userDefaultValues:h,setFormState:y,handleChange:_,handleNumberValueChange:S,setSubnets:k,setSecurityGroups:j,onSelectLCCScript:x,setFormValidationErrors:w,setEnableVPCSetting:T,setRoleArn:P})=>{const{pluginEnvironment:M}=ze(),[I,N]=(0,n.useState)(!1),[O,F]=(0,n.useState)(!1),[J,D]=(0,n.useState)(!1),[A,V]=(0,n.useState)(!1),R=e=>{const t=e.target.name,n=De(e.target.value);w({...r,["s3_input"===t?"s3InputFolderError":"s3OutputFolderError"]:n})},L=e=>{const t=e.target.name,n=Ae(e.target.value);w({...r,["sm_output_kms_key"===t?"outputKMSError":"ebsKMSError"]:n})};return o().createElement("div",{className:G},o().createElement(K,{"aria-label":"role_arn",name:"role_arn",disabled:A,readOnly:e,required:!0,labelInfo:qe.RoleArn,errorMessage:r.roleError,placeholder:qe.Placeholders.RolePlaceHolder,onChange:_,value:t.role_arn,onBlur:e=>{const{value:t}=e.target,n=Je(t);P(t),w({...r,roleError:n})},toolTipText:M.isStudioOrJupyterLab?He.RoleArnTooltip:Ze.RoleArnTooltip}),o().createElement(K,{name:"s3_input",onChange:_,required:!0,disabled:A,readOnly:e,value:t.s3_input,placeholder:qe.Placeholders.S3BucketPlaceHolder,labelInfo:qe.s3InputFolder,errorMessage:r.s3InputFolderError,onBlur:R,toolTipText:M.isStudioOrJupyterLab?He.InputFolderTooltip:Ze.InputFolderTooltip}),!e&&o().createElement("div",{className:Z},o().createElement(f.Checkbox,{"data-testid":"input_cross_account_id",name:"input_cross_account_id",className:Y,color:"primary",checked:O,onChange:e=>{const r=e.target.checked;F(r),y({...t,s3_input_account_id:""})}}),o().createElement("label",null,qe.inputInDifferentAccount)),(e||O)&&o().createElement(o().Fragment,null,o().createElement(K,{name:"s3_input_account_id",onChange:_,required:!1,readOnly:e,disabled:A,value:t.s3_input_account_id,labelInfo:qe.inputInDifferentAccountLabel,onBlur:e=>{y({...t,s3_input_account_id:e.target.value})}})),o().createElement(K,{name:"s3_output",onChange:_,required:!0,disabled:A,readOnly:e,value:t.s3_output,placeholder:qe.Placeholders.S3BucketPlaceHolder,labelInfo:qe.s3OutputFolder,errorMessage:r.s3OutputFolderError,onBlur:R,toolTipText:M.isStudioOrJupyterLab?He.OutputFolderTooltip:Ze.OutputFolderTooltip}),!e&&o().createElement("div",{className:Z},o().createElement(f.Checkbox,{"data-testid":"output_cross_account_id",name:"output_cross_account_id",className:Y,color:"primary",checked:J,onChange:e=>{const r=e.target.checked;D(r),y({...t,s3_output_account_id:""})}}),o().createElement("label",null,qe.outputInDifferentAccount)),(e||J)&&o().createElement(o().Fragment,null,o().createElement(K,{name:"s3_output_account_id",onChange:_,required:!1,readOnly:e,disabled:A,value:t.s3_output_account_id,labelInfo:qe.outputInDifferentAccountLabel,onBlur:e=>{y({...t,s3_output_account_id:e.target.value})}})),o().createElement("div",{className:Z},o().createElement(f.Checkbox,{"data-testid":"enable_network_isolation_checkbox",name:"enable_network_isolation_checkbox",className:Y,color:"primary",disabled:e,checked:t.enable_network_isolation,onChange:e=>{y({...t,enable_network_isolation:e.target.checked})}}),o().createElement("label",null,qe.enableNetworkIsolation),o().createElement(C,{classes:{popperInteractive:W},title:Ye},o().createElement(E.Z,{fontSize:"small"}))),!e&&o().createElement("div",{className:Z},o().createElement(f.Checkbox,{"data-testid":"kms_checkbox",name:"kms_checkbox",className:Y,color:"primary",checked:I,onChange:e=>{const n=e.target.checked;N(n);const o=n?h.sm_output_kms_key:"",a=n?h.sm_volume_kms_key:"";y({...t,sm_output_kms_key:o,sm_volume_kms_key:a}),w({...r,outputKMSError:Ae(o),ebsKMSError:Ae(a)})}}),o().createElement("label",null,qe.enableEncryption),o().createElement(C,{classes:{popperInteractive:W},title:We},o().createElement(E.Z,{fontSize:"small"}))),(e||I)&&o().createElement(o().Fragment,null,o().createElement(K,{name:"sm_output_kms_key",onChange:_,required:!1,readOnly:e,disabled:A,value:t.sm_output_kms_key,placeholder:e?qe.Placeholders.NoneSelected:qe.enterKMSArnOrID,labelInfo:qe.kmsKey,errorMessage:r.outputKMSError,onBlur:L,toolTipText:e?void 0:Ze.kmsKeyTooltip}),o().createElement(K,{name:"sm_volume_kms_key",onChange:_,required:!1,readOnly:e,disabled:A,value:t.sm_volume_kms_key,placeholder:e?qe.Placeholders.NoneSelected:qe.enterKMSArnOrID,labelInfo:qe.ebsKey,errorMessage:r.ebsKMSError,onBlur:L,toolTipText:e?void 0:Ze.ebsKeyTooltip})),m&&!e&&o().createElement(oe,{isChecked:g,setChecked:T,initialSecurityGroups:d,initialSubnets:c,availableSubnets:u,formState:t,formErrors:r,setFormErrors:w,setFormState:y,"data-testid":"vpc-checkbox"}),(m&&g||e)&&o().createElement(o().Fragment,null,o().createElement(Ce,{required:!0,name:"vpc_subnets",disabled:e||M.isStudioOrJupyterLab&&0===u.length,label:qe.subnet,options:u,value:t.vpc_subnets,onChange:(e,n,o)=>{const[a,i]=((e,t)=>{if(0===e.length)return 0===t.length?["",""]:[Oe.AdvancedOptions.SubnetMinError,void 0];if(e&&e.length>0){if(e.length>16)return[Oe.AdvancedOptions.SubnetsMaxError,void 0];for(const t of e){if(t.length>32)return[Oe.AdvancedOptions.SubnetLengthError,void 0];if(!Pe.test(t))return[Oe.AdvancedOptions.SubnetsFormatError,void 0]}if(0===t.length)return["",Oe.AdvancedOptions.SecurityGroupMinError]}return["",void 0]})(n,t.vpc_security_group_ids);k(n),w({...r,securityGroupError:null!=i?i:r.securityGroupError,subnetError:null!=a?a:""})},errorMessage:r.subnetError,placeholder:`${qe.Placeholders.SelectPrivateSubnets}`,tooltip:M.isStudio?He.SubnetTooltip:Ze.SubnetTooltip,disabledTooltip:`${qe.Placeholders.NoPrivateSubnets}`,freeSolo:!0}),o().createElement(Ce,{required:!0,className:"securityGroupSelector",name:"vpc_security_group_ids",disabled:e||M.isStudioOrJupyterLab&&0===s.length,label:qe.securityGroup,options:s,value:t.vpc_security_group_ids,onChange:(e,n,o)=>{const[a,i]=((e,t)=>{if(0===e.length)return 0===t.length?["",""]:[Oe.AdvancedOptions.SecurityGroupMinError,void 0];if(e.length>0){if(e.length>5)return[Oe.AdvancedOptions.SecurityGroupsMaxError,void 0];for(const t of e){if(!t.startsWith("sg-"))return[Oe.AdvancedOptions.SecurityGroupSGError,void 0];if(t.length>32)return[Oe.AdvancedOptions.SecurityGroupLengthError,void 0];if(!Pe.test(t))return[Oe.AdvancedOptions.SecurityGroupFormatError,void 0]}if(0===t.length)return["",Oe.AdvancedOptions.SubnetMinError]}return["",void 0]})(n,t.vpc_subnets);j(n),w({...r,securityGroupError:null!=a?a:"",subnetError:null!=i?i:r.subnetError})},errorMessage:r.securityGroupError,placeholder:`${qe.Placeholders.selectOrAdd} ${qe.securityGroup}`,tooltip:M.isStudio?He.SecurityGroupsTooltip:Ze.SecurityGroupsTooltip,disabledTooltip:`${qe.Placeholders.No} ${qe.securityGroup}`,freeSolo:!0})),M.isStudioOrJupyterLab&&o().createElement("div",{className:Q},o().createElement(Ge.Z,{id:"startup-script-select-label"},qe.startUpScript,o().createElement(C,{title:Qe},o().createElement(E.Z,{fontSize:"small"}))),o().createElement(Ke.Z,{labelId:"startup-script-select-label",id:"startup-script-select",disabled:A,readOnly:e,value:t.sm_lcc_init_script_arn,onChange:e=>x(e.target.value)},l&&l.map((e=>o().createElement(Be.Z,{key:e,value:e},e))))),o().createElement(Se,{isButtonDisabled:e||a.length>=48||!!r.environmentVariablesError,allFieldsDisabled:e,environmentVariables:a,setEnvironmentVariables:i,formErrors:r,setFormErrors:w}),o().createElement("div",null,o().createElement(K,{placeholder:e?qe.Placeholders.NoneSelected:qe.efsPlaceholder,labelInfo:qe.efsLabel,required:!1,value:t.sm_init_script,name:"sm_init_script",readOnly:e,disabled:A,errorMessage:r.efsFilePathError,onChange:_,onBlur:e=>{const t=e.target.value;0===t.trim().length?w({...r,efsFilePathError:""}):(async e=>{const t=v.URLExt.join(p.baseUrl,"/validate_volume_path");V(!0);const n=await b.ServerConnection.makeRequest(t,{method:"POST",body:JSON.stringify({file_path:e})},p);V(!1),200!==n.status||!0===(await n.json()).file_path_exist?w({...r,efsFilePathError:""}):w({...r,efsFilePathError:Ue.AdvancedOptions.EFSFilePathError})})(t)},toolTipText:e?void 0:M.isStudio?He.InitialScriptTooltip:Ze.InitialScriptTooltip})),o().createElement(K,{name:"max_retry_attempts",type:"number",onChange:S,required:!0,disabled:A,readOnly:e,value:t.max_retry_attempts,placeholder:qe.maxRetryAttempts,labelInfo:qe.maxRetryAttempts,errorMessage:r.maxRetryAttemptsError,onBlur:e=>{const t=(e=>{const t=parseInt(e);return isNaN(t)||t<0||t>30?Oe.AdvancedOptions.MaxRetryAttemptsError:""})(e.target.value);w({...r,maxRetryAttemptsError:t})},toolTipText:Ze.MaxRetryAttempts}),o().createElement(K,{name:"max_run_time_in_seconds",type:"number",onChange:S,required:!0,disabled:A,readOnly:e,value:t.max_run_time_in_seconds,placeholder:qe.maxRunTimeInSeconds,labelInfo:qe.maxRunTimeInSeconds,errorMessage:r.maxRunTimeInSecondsError,onBlur:e=>{const t=(e=>{const t=parseInt(e);return isNaN(t)||t<0?Oe.AdvancedOptions.MaxRunTimeInSecondsError:""})(e.target.value);w({...r,maxRunTimeInSecondsError:t})},toolTipText:Ze.MaxRunTimeInSeconds}))},et="No script",tt=new Set(["sm_kernel","sm_image","sm_lcc_init_script_arn","role_arn","vpc_security_group_ids","vpc_subnets","s3_input","s3_output","sm_init_script","sm_output_kms_key","sm_volume_kms_key","max_run_time_in_seconds","max_retry_attempts","enable_network_isolation"]),rt=(e,t,r,n)=>{var o,a;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e[n]?e[n].split(","):[]}else if(r===i.JobsView.CreateForm){if(e&&n in e){const t=e[n];return t?t.split(","):[]}const r=null===(o=null==t?void 0:t.find((e=>e.name===n)))||void 0===o?void 0:o.value;return(null===(a=null==r?void 0:r.filter((e=>e.is_selected)))||void 0===a?void 0:a.map((e=>e.name)))||[]}return[]},nt=(e,t,r,n)=>{var o;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e[n]}else if(r===i.JobsView.CreateForm)return e&&n in e?e[n]:(null===(o=null==t?void 0:t.find((e=>e.name===n)))||void 0===o?void 0:o.value)||"";return""},ot=(e,t,r,n)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e[n]}else if(t===i.JobsView.CreateForm&&e&&n in e)return e[n];return r},at=(e,t,r)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e[r]}else if(t===i.JobsView.CreateForm&&e&&r in e)return e[r];return""},it=({label:e,value:t,options:r,onChange:n,freeSolo:a,customListItemRender:i,renderInput:l,...s})=>{var u;const c=Object.fromEntries(r.map((e=>[e.value,e])));let d=t;return!a&&"string"==typeof t&&t in c&&(d=c[t]),o().createElement(o().Fragment,null,o().createElement(je.Z,{...s,id:`${e}-selectinput`,renderOption:(e,t,r)=>o().createElement("li",{...e},i?i(t,t.label,r.selected):t.label),componentsProps:{...s.componentsProps,popupIndicator:{...null===(u=s.componentsProps)||void 0===u?void 0:u.popupIndicator,size:"small"}},options:r,onChange:(e,t,r)=>{(t&&"string"!=typeof t||a)&&n&&n(t||"")},value:d,renderInput:l||(e=>o().createElement(xe.Z,{...e,variant:"outlined",size:"small",margin:"dense"}))}))},lt=({label:e,required:t=!0,toolTipText:r,toolTipArea:n,errorMessage:a,...i})=>{const l=n&&o().createElement("div",null,o().createElement("span",{className:H},n.descriptionText),n.toolTipComponent);return o().createElement("div",{className:T},o().createElement("div",{className:M},o().createElement("label",{className:J(t)},e),(r||n)&&!i.readOnly&&o().createElement(C,{title:l||r||"",className:I,disableInteractive:null===n},o().createElement(E.Z,null))),o().createElement(it,{label:e,disableClearable:!0,...i}))},st=y.css`
  display: flex;
  flex-direction: column;
  padding: 10px;
`,ut=y.css`
  display: flex;
  flex-direction: column;
  gap: 20px;
`,ct=y.css`
  display: flex;
  flex-direction: column;
`,dt=(y.css`
  transform: rotate(90deg);
`,y.css`
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`),mt=y.css`
  font-size: var(--jp-ui-font-size0);
  min-width: max-content;
`,pt=y.css`
  font-size: var(--jp-ui-font-size0);
  color: var(--jp-inverse-layout-color4);
  padding-right: 5px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
`,vt=y.css`
  width: 100%;
`,bt=y.css`
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  &[data-selected='true'] {
    background-image: var(--jp-check-icon);
    background-size: 15px;
    background-repeat: no-repeat;
    background-position: 100% center;
  }
  & > p {
    max-width: calc(100% - 10px);
  }
`,gt=(e,t,r)=>o().createElement("span",{className:vt},o().createElement("div",{className:bt,"data-selected":r},o().createElement("p",null,t||e.label)),ht(e.optionMetadata&&e.optionMetadata.description)),ht=e=>{if(!e)return;const t=e.match(/(((https?:\/\/)|(www\.))[^\s]+)/g);if(t){console.log("links",t);for(const r of t)e=e.replace(r," ")}const r=e.trim();return o().createElement("div",{className:dt},o().createElement("span",{className:pt},r),t&&t.map((e=>o().createElement(V,{className:mt,key:e,href:e,target:D.External},l.KernelSelector.imageSelectorOption.linkText))))};r(9850);const ft=["datascience-1.0","sagemaker-data-science-38","1.8.1-cpu-py36","pytorch-1.8-gpu-py36","sagemaker-sparkmagic","tensorflow-2.6-cpu-py38-ubuntu20.04-v1","tensorflow-2.6-gpu-py38-cu112-ubuntu20.04-v1","sagemaker-sparkanalytics-v1"];var Et;async function yt(e,t){if(e.endsWith(".ipynb"))try{return(await t.get(e)).content.metadata.kernelspec.name}catch(e){return""}return""}!function(e){e.Custom="customImage",e.Sagemaker="smeImage",e.Session="session"}(Et||(Et={}));const _t={smeImage:"Sagemaker Image",customImage:"Custom Image",prefered:"Use image from preferred session",session:"Use image from other session"};function St(e,t,r){const n=Object.values(e).filter((e=>{const n=e.arnEnvironment.split("/")[1];return r?(null==e?void 0:e.group)===t&&ft.includes(n):((null==e?void 0:e.group)!==Et.Sagemaker||!e.label.includes("Geospatial"))&&(null==e?void 0:e.group)===t}));return{label:_t[t],value:"",options:n.map((e=>({label:e.label,value:t===Et.Session?e.label:e.arnEnvironment,group:_t[t],optionMetadata:e,options:e.versionOptions})))}}const kt=l.ScheduleNoteBook.MainPanel.Tooltips,jt=l.ScheduleNoteBook.MainPanel.StudioTooltips,xt=({isDisabled:e,formState:t,formErrors:r,setFormState:a,setFormErrors:s,model:u,jobsView:c,requestClient:d,contentsManager:m})=>{var p,g;const{pluginEnvironment:h}=ze(),[f,E]=(0,n.useState)({arnEnvironment:null,kernel:null,version:null}),[y,_]=(0,n.useState)({});(0,n.useEffect)((()=>{(async function(e){const t=v.URLExt.join(e.baseUrl,"api/kernelspecs"),r=await b.ServerConnection.makeRequest(t,{},e);if(200===r.status)return await r.json()})(d).then((async e=>{var t;e&&_(function(e){const t={},r=e.kernelspecs;return Object.values(r).forEach((e=>{var r;if(!e)return;const n=(null===(r=e.spec)||void 0===r?void 0:r.metadata)?e.spec.metadata.sme_metadata:null,{imageName:o,kernelName:a}=function(e){try{if(!$()(e)||0===e.length)return{imageName:null,kernelName:null};const[t,r]=e.split("(");return{imageName:r&&r.slice(0,-1).split("/")[0],kernelName:t&&t.slice(0,-1)}}catch(e){return{imageName:null,kernelName:null}}}(e.spec.display_name),{kernel:i,arnEnvironment:l,version:s}=z(e.name);if(!(i&&l&&o&&a))return;const u={arnEnvironment:l,kernelOptions:[{label:a,value:i}],versionOptions:s?[{label:`v${s}`,value:s}]:void 0,label:s?`${o} v${s}`:o,description:(null==n?void 0:n.description)?n.description:void 0,group:n&&n.is_template?Et.Sagemaker:Et.Custom};if(t[l]){const{kernelOptions:e}=t[l];if(!e.some((e=>e.value===i))){const r=[...e,{label:a,value:i}];t[l].kernelOptions=r}if(s){const{versionOptions:e}=t[l];if(!e.some((e=>e.value===s))){const r={label:`v${s}`,value:s.toString()},n=Array.isArray(e)?[...e,r]:[r];t[l].versionOptions=n}}}else t[l]=u})),t}(e));const r=await yt(u.inputFile,m),n=r in(null!==(t=null==e?void 0:e.kernelspecs)&&void 0!==t?t:{})?r:"",o=((e,t,r)=>{if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}return{kernel:null,arnEnvironment:null,version:null}}if(r===i.JobsView.CreateForm){if(e&&"sm_image"in e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}return z(t)||{kernel:null,arnEnvironment:null,version:null}}return z(t)||{kernel:null,arnEnvironment:null,version:null}})(u.runtimeEnvironmentParameters,n,c);E(o),a((e=>({...e,sm_kernel:o.kernel||"",sm_image:o.arnEnvironment||""})))}))}),[]);const S=[...null!==(p=St(y,Et.Sagemaker,!1).options)&&void 0!==p?p:[],...null!==(g=St(y,Et.Custom).options)&&void 0!==g?g:[]],k=(0,n.useMemo)((()=>{var e;return f.arnEnvironment&&(null===(e=y[f.arnEnvironment])||void 0===e?void 0:e.kernelOptions)||[]}),[y,f]),j=!!r.jobEnvironmentError,x=o().createElement("div",{className:F},o().createElement(ae.Z,{severity:"error"},r.jobEnvironmentError));return(0,n.useEffect)((()=>{f.arnEnvironment&&f.kernel&&r.jobEnvironmentError&&s({...r,jobEnvironmentError:""})}),[f.arnEnvironment,f.kernel]),0===Object.keys(y).length?null:o().createElement("div",{className:st},o().createElement("div",{className:ut},o().createElement("div",{className:ct},o().createElement(lt,{"data-testid":"sm_image_dropdown",options:S,value:f.arnEnvironment,label:l.ImageSelector.label,customListItemRender:gt,onChange:(e,r)=>{var n;if(!e||"string"==typeof e)return;const o=(null===(n=e.optionMetadata)||void 0===n?void 0:n.kernelOptions)||[],i=o.length>0?o[0].value:null,l=r?r.value:null;a({...t,sm_image:e.value+(l?"/"+l:""),sm_kernel:null!=i?i:""}),E({arnEnvironment:e.value,kernel:i,version:l})},readOnly:e,groupBy:e=>{var t;return null!==(t=e.group)&&void 0!==t?t:""},toolTipText:h.isStudio?jt.ImageTooltipText:kt.ImageTooltipText}),r.jobEnvironmentError&&o().createElement("div",{className:O},j&&x)),o().createElement(lt,{options:k,value:f.kernel,label:l.KernelSelector.label,onChange:e=>{e&&"string"!=typeof e&&e&&(a({...t,sm_kernel:e.value}),E({...f,kernel:e.value}))},readOnly:e,toolTipText:h.isStudio?jt.KernelTooltipText:kt.KernelTooltipText})))},wt=l.ScheduleNoteBook.MainPanel.AdvancedOptions,Ct=l.ScheduleNoteBook.MainPanel.Tooltips,Tt=({setFormState:e,formState:t,isDisabled:r,formErrors:a,setFormErrors:i,model:l,executionEnvironments:s})=>{const u=(0,n.useMemo)((()=>((e,t)=>{var r,n;if(e){const{sm_kernel:t,sm_image:r}=e;return z(`${t}__SAGEMAKER_INTERNAL__${r}`)}const o=null===(r=null==t?void 0:t.find((e=>"image"===e.name)))||void 0===r?void 0:r.value,a=null===(n=null==t?void 0:t.find((e=>"kernel"===e.name)))||void 0===n?void 0:n.value;return R(o)&&R(a)?z(`${a}__SAGEMAKER_INTERNAL__${o}`):{kernel:null,arnEnvironment:null,version:null}})(l.runtimeEnvironmentParameters,null==s?void 0:s.auto_detected_config)),[]);(0,n.useEffect)((()=>{e({...t,sm_kernel:u.kernel||"",sm_image:u.arnEnvironment||""})}),[u]);const c=r=>{const n=r.target.name,o=r.target.value;e({...t,[n]:o})};return o().createElement("div",{className:G},o().createElement(K,{name:"sm_image",onChange:c,readOnly:r,required:!0,value:t.sm_image,placeholder:wt.Placeholders.ImagePlaceHolder,labelInfo:wt.Image,errorMessage:a.ImageError,onBlur:e=>{const{value:t}=e.target,r=t.length<=0?Oe.AdvancedOptions.ImageError:"";i({...a,ImageError:r})},toolTipText:Ct.ImageTooltipText}),o().createElement(K,{name:"sm_kernel",onChange:c,readOnly:r,required:!0,value:t.sm_kernel,placeholder:wt.Placeholders.KernelPlaceHolder,labelInfo:wt.Kernel,errorMessage:a.KernelError,onBlur:e=>{const{value:t}=e.target,r=t.length<=0?Oe.AdvancedOptions.KernelError:"";i({...a,KernelError:r})},toolTipText:Ct.KernelTooltipText}))},Pt=l.ScheduleNoteBook.MainPanel.Tooltips,Mt=({setFormState:e,formState:t,isDisabled:r,formErrors:a,setFormErrors:i,contentsManager:s,model:u})=>{const[c,d]=(0,n.useState)([]),[m,p]=(0,n.useState)([]),g=async()=>{const e=b.ServerConnection.makeSettings(),t=v.URLExt.join(e.baseUrl,"/sagemaker_images"),r=await b.ServerConnection.makeRequest(t,{},e);return 200==r.status?(await r.json()).map((e=>({label:e.image_display_name,value:e.image_arn}))):[]},h=async()=>{const e=b.ServerConnection.makeSettings(),t=v.URLExt.join(e.baseUrl,"/api/kernelspecs"),r=await b.ServerConnection.makeRequest(t,{},e);let n=null;const o=[],a=[];if(200===r.status){const e=await r.json();n=e.default,e.kernelspecs&&Object.values(e.kernelspecs).forEach((e=>{if(e){o.push(e.name);let t=e.name;e.spec&&(t=e.spec.display_name),a.push({label:t,value:e.name})}}))}return{defaultKernelName:n,kernelNames:o,kernelOptions:a}};return(0,n.useEffect)((()=>{Promise.all([yt(u.inputFile,s),g(),h()]).then((t=>{const r=t[0],n=t[1],o=t[2];let a,i;n&&n.length>0&&d(n),u.runtimeEnvironmentParameters&&u.runtimeEnvironmentParameters.sm_image?a=u.runtimeEnvironmentParameters.sm_image:n&&n.length>0&&(a=n[0].value),o&&o.kernelOptions&&o.kernelOptions.length>0&&p(o.kernelOptions),i=u.runtimeEnvironmentParameters&&u.runtimeEnvironmentParameters.sm_kernel?u.runtimeEnvironmentParameters.sm_kernel:o.kernelNames.indexOf(r)>=0?r:o.defaultKernelName||"",e((e=>({...e,sm_image:null!=a?a:"",sm_kernel:null!=i?i:""})))})).catch((e=>console.error(e)))}),[]),o().createElement("div",{className:G},o().createElement(lt,{"data-testid":"sm_image_dropdown",options:c,value:t.sm_image,label:l.ImageSelector.label,onChange:r=>{r&&"string"!=typeof r&&e({...t,sm_image:r.value})},readOnly:r,toolTipText:Pt.ImageTooltipText,required:!0}),o().createElement(lt,{"data-testid":"sm_kernel_dropdown",options:m,value:t.sm_kernel,label:l.KernelSelector.label,onChange:r=>{r&&"string"!=typeof r&&e({...t,sm_kernel:r.value})},readOnly:r,toolTipText:Pt.KernelTooltipText,required:!0}))},It=e=>{const{pluginEnvironment:t}=ze();return o().createElement(o().Fragment,null,t.isStudio&&o().createElement(xt,{...e}),t.isJupyterLab&&o().createElement(Mt,{...e}),t.isLocalJL&&o().createElement(Tt,{...e}))},Nt=e=>{const{executionEnvironments:t,settingRegistry:r,jobsView:a,requestClient:l,errors:s,handleErrorsChange:u,model:d,handleModelChange:m}=e,p=(0,n.useMemo)((()=>{return e=null==t?void 0:t.auto_detected_config,a===i.JobsView.CreateForm&&(null===(r=null==e?void 0:e.find((e=>"app_network_access_type"===e.name)))||void 0===r?void 0:r.value)||"";var e,r}),[]),v=a===i.JobsView.JobDefinitionDetail||a===i.JobsView.JobDetail,b=(0,n.useMemo)((()=>{var e,r;const n=[],o=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"lcc_arn"===e.name)))||void 0===r?void 0:r.value)||[];n.push(et),n.push(...o);const l=(s=d.runtimeEnvironmentParameters,((u=a)===i.JobsView.JobDetail||u===i.JobsView.JobDefinitionDetail)&&s&&s.sm_lcc_init_script_arn||et);var s,u;return d.runtimeEnvironmentParameters&&l!==et&&n.push(l),{allLCCOptions:n,selectedLccValue:l}}),[]),g=(0,n.useMemo)((()=>((e,t,r)=>{var n;if(r===i.JobsView.JobDetail||r===i.JobsView.JobDefinitionDetail){if(e)return e.role_arn}else if(r===i.JobsView.CreateForm){if(e&&"role_arn"in e)return e.role_arn;const r=null===(n=null==t?void 0:t.find((e=>"role_arn"===e.name)))||void 0===n?void 0:n.value;if((null==r?void 0:r.length)>0)return r[0]}return""})(d.runtimeEnvironmentParameters,t.auto_detected_config,a)),[]),h=(0,n.useMemo)((()=>nt(d.runtimeEnvironmentParameters,t.auto_detected_config,a,"s3_output")),[]),f=(0,n.useMemo)((()=>nt(d.runtimeEnvironmentParameters,t.auto_detected_config,a,"s3_input")),[]),E=(0,n.useMemo)((()=>ot(d.runtimeEnvironmentParameters,a,1,"max_retry_attempts")),[]),y=(0,n.useMemo)((()=>((e,t,r)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return Boolean(e[r])}else if(t===i.JobsView.CreateForm&&e&&r in e)return Boolean(e[r]);return!1})(d.runtimeEnvironmentParameters,a,"enable_network_isolation")),[]),_=(0,n.useMemo)((()=>ot(d.runtimeEnvironmentParameters,a,172800,"max_run_time_in_seconds")),[]),S=(0,n.useMemo)((()=>{var e,r;const n=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"vpc_security_group_ids"===e.name)))||void 0===r?void 0:r.value)||[];return null==n?void 0:n.map((e=>e.name))}),[]),k=(0,n.useMemo)((()=>{var e,r;const n=(null===(r=null===(e=t.auto_detected_config)||void 0===e?void 0:e.find((e=>"vpc_subnets"===e.name)))||void 0===r?void 0:r.value)||[];return null==n?void 0:n.map((e=>e.name))}),[]),j=(0,n.useMemo)((()=>p===c.PublicInternetOnly?{securityGroups:[],subnets:[]}:{securityGroups:0===k.length&&a===i.JobsView.CreateForm?[]:rt(d.runtimeEnvironmentParameters,t.auto_detected_config,a,"vpc_security_group_ids"),subnets:rt(d.runtimeEnvironmentParameters,t.auto_detected_config,a,"vpc_subnets")}),[]),x=(0,n.useMemo)((()=>((e,t)=>{if(t===i.JobsView.JobDetail||t===i.JobsView.JobDefinitionDetail){if(e)return e.sm_init_script}else if(t===i.JobsView.CreateForm&&e&&"sm_init_script"in e)return e.sm_init_script;return""})(d.runtimeEnvironmentParameters,a)),[]),w=(0,n.useMemo)((()=>(e=>{const t=[];if(e)for(const r in e)if(!tt.has(r)){const n={key:r,value:e[r]};t.push(n)}return t})(d.runtimeEnvironmentParameters)),[]),C=(0,n.useMemo)((()=>at(d.runtimeEnvironmentParameters,a,"sm_output_kms_key")),[]),T=(0,n.useMemo)((()=>at(d.runtimeEnvironmentParameters,a,"sm_volume_kms_key")),[]),P=(0,n.useMemo)((()=>{if(p===c.PublicInternetOnly)return!1;const e=j.subnets;return 0!==k.length&&(0===e.length&&k.length,!0)}),[]),[M,I]=(0,n.useState)({sm_lcc_init_script_arn:b.selectedLccValue||"",role_arn:g||"",vpc_security_group_ids:j.securityGroups||"",vpc_subnets:j.subnets||"",s3_input:f||"",s3_input_account_id:"",s3_output:h||"",s3_output_account_id:"",sm_kernel:"",sm_image:"",sm_init_script:x||"",sm_output_kms_key:C||"",sm_volume_kms_key:T||"",max_retry_attempts:E,max_run_time_in_seconds:_,enable_network_isolation:y}),[O,F]=(0,n.useState)({...M,sm_output_kms_key:"",sm_volume_kms_key:""});(0,n.useEffect)((()=>{const e=(e=>e&&0===e.length?`${Fe.RequiresPrivateSubnet} ${Fe.NoPrivateSubnetsInSageMakerDomain}`:"")(k),t=(r=j.subnets)&&0===r.length?`${Fe.RequiresPrivateSubnet} ${Fe.NoPrivateSubnetsInSageMakerDomain}. ${Fe.YouMayChooseOtherSubnets}`:"";var r;u({...s,roleError:Je(g),s3InputFolderError:De(f),s3OutputFolderError:De(h),environmentsStillLoading:"",kernelsStillLoading:"",subnetError:P&&(e||t)||""})}),[]);const[J,D]=(0,n.useState)();(0,n.useEffect)((()=>{(async function(e){return(await e.get("@amzn/sagemaker-jupyter-scheduler:advanced-options","advancedOptions")).composite})(r).then((e=>{D(e)}))}),[]),(0,n.useEffect)((()=>{var e,t,r,n,o,a;let i={},l={},c={};const d=null!==(e=null==J?void 0:J.enable_network_isolation)&&void 0!==e&&e;i={...i,enable_network_isolation:d};const m=null!==(t=null==J?void 0:J.role_arn)&&void 0!==t?t:"";m&&m!==g&&(i={...i,role_arn:m},l={...l,roleError:Je(m)});const p=null!==(r=null==J?void 0:J.s3_input)&&void 0!==r?r:"";p&&p!==f&&(i={...i,s3_input:p},l={...l,s3InputFolderError:De(p)});const b=null!==(n=null==J?void 0:J.s3_output)&&void 0!==n?n:"";b&&b!==h&&(i={...i,s3_output:b},l={...l,s3OutputFolderError:De(b)});const E=null!==(o=null==J?void 0:J.sm_output_kms_key)&&void 0!==o?o:"";E&&E!==C&&(c={...c,sm_output_kms_key:E});const y=null!==(a=null==J?void 0:J.sm_volume_kms_key)&&void 0!==a?a:"";y&&y!==T&&(c={...c,sm_volume_kms_key:y}),c={...i,...c},Object.keys(i).length>0&&!v&&F({...O,...i}),Object.keys(c).length>0&&I({...M,...c}),Object.keys(l).length>0&&u({...s,...l})}),[J]);const[A,V]=(0,n.useState)(w),[R,L]=(0,n.useState)(P),$=(0,n.useMemo)((()=>{const e={};return null==A||A.map((t=>{const{key:r,value:n}=t;0!==r.trim().length&&0!==n.trim().length&&(e[r]=n)})),e}),[A]);return(0,n.useEffect)((()=>{var e,t;const r=(null===(e=O.vpc_security_group_ids)||void 0===e?void 0:e.join(","))||"",n=(null===(t=O.vpc_subnets)||void 0===t?void 0:t.join(","))||"";m({...d,runtimeEnvironmentParameters:{...O,vpc_security_group_ids:r,vpc_subnets:n,...$}})}),[O,$]),o().createElement("div",{className:N(v)},o().createElement(It,{isDisabled:v,formState:O,setFormState:F,formErrors:s,setFormErrors:u,...e}),o().createElement(Xe,{isDisabled:v,formState:O,setFormState:F,handleChange:e=>{const t=e.target.name,r=e.target.value;F({...O,[t]:r})},handleNumberValueChange:e=>{const t=e.target.name,r=parseInt(e.target.value);F({...O,[t]:isNaN(r)?"":r})},requestClient:l,formErrors:s,setFormValidationErrors:u,environmentVariables:A,userDefaultValues:M,setEnvironmentVariables:V,lccOptions:b.allLCCOptions,availableSecurityGroups:S,availableSubnets:k,initialSecurityGroups:j.securityGroups,initialSubnets:j.subnets,setSubnets:e=>{F({...O,vpc_subnets:e})},setRoleArn:e=>{F({...O,role_arn:e})},setSecurityGroups:e=>{F({...O,vpc_security_group_ids:e})},onSelectLCCScript:e=>{F({...O,sm_lcc_init_script_arn:e})},isVPCDomain:p===c.VpcOnly,enableVPCSetting:R,setEnableVPCSetting:L}))};var Ot=r(2453);function Ft(e){return getComputedStyle(document.body).getPropertyValue(e).trim()}function Jt(){const e=document.body.getAttribute("data-jp-theme-light");return(0,Ot.Z)({spacing:4,components:{MuiButton:{defaultProps:{size:"small"}},MuiFilledInput:{defaultProps:{margin:"dense"}},MuiFormControl:{defaultProps:{margin:"dense",size:"small"}},MuiFormHelperText:{defaultProps:{margin:"dense"}},MuiIconButton:{defaultProps:{size:"small"}},MuiInputBase:{defaultProps:{margin:"dense",size:"small"}},MuiInputLabel:{defaultProps:{margin:"dense"},styleOverrides:{root:{display:"flex",alignItems:"center",color:"var(--jp-ui-font-color0)",gap:"6px"}}},MuiListItem:{defaultProps:{dense:!0}},MuiOutlinedInput:{defaultProps:{margin:"dense"}},MuiFab:{defaultProps:{size:"small"}},MuiAutocomplete:{defaultProps:{componentsProps:{paper:{elevation:4}}}},MuiTable:{defaultProps:{size:"small"}},MuiTextField:{defaultProps:{margin:"dense",size:"small"}},MuiToolbar:{defaultProps:{variant:"dense"}}},palette:{background:{paper:Ft("--jp-layout-color1"),default:Ft("--jp-layout-color1")},mode:"true"===e?"light":"dark",primary:{main:Ft("--jp-brand-color1"),light:Ft("--jp-brand-color2"),dark:Ft("--jp-brand-color0")},error:{main:Ft("--jp-error-color1"),light:Ft("--jp-error-color2"),dark:Ft("--jp-error-color0")},warning:{main:Ft("--jp-warn-color1"),light:Ft("--jp-warn-color2"),dark:Ft("--jp-warn-color0")},success:{main:Ft("--jp-success-color1"),light:Ft("--jp-success-color2"),dark:Ft("--jp-success-color0")},text:{primary:Ft("--jp-ui-font-color1"),secondary:Ft("--jp-ui-font-color2"),disabled:Ft("--jp-ui-font-color3")}},shape:{borderRadius:2},typography:{fontFamily:Ft("--jp-ui-font-family"),fontSize:12,htmlFontSize:16,button:{textTransform:"capitalize"}}})}const Dt=({requestClient:e,contentsManager:t,commands:r,jobsView:a,errors:c,handleErrorsChange:g,...h})=>{const{pluginEnvironment:f}=ze(),[E,y]=(0,n.useState)("");(0,n.useEffect)((()=>{const t={...c,environmentsStillLoading:"EnvironmentsStillLoadingError",kernelsStillLoading:"KernelsStillLoadingError"};g(t),a===i.JobsView.CreateForm?(async()=>{const t=v.URLExt.join(e.baseUrl,"/advanced_environments"),n=await b.ServerConnection.makeRequest(t,{},e);if(200!==n.status&&f.isLocalJL){const e=(await n.json()).error_code;throw Object.values(s).indexOf(e)>=0&&(async e=>{const t=o().createElement(o().Fragment,null,l.Dialog.awsCredentialsError.body.text.map(((e,t)=>o().createElement("p",{key:t,className:q},((e,t)=>{const r=e.split("%");return o().createElement(o().Fragment,null,r.map((e=>{if(e.startsWith("{")){const[r,...n]=e.replace("{","").split("}"),a=t[r],i=n.join("");return a?o().createElement(o().Fragment,null,o().createElement(V,{key:r,href:a.linkHref,target:D.External},a.linkString),i):o().createElement(o().Fragment,null,e)}return o().createElement(o().Fragment,null,e)})))})(e,l.Dialog.awsCredentialsError.body.links))))),r=new d.Dialog({title:l.Dialog.awsCredentialsError.title,body:t,buttons:[d.Dialog.cancelButton(),d.Dialog.okButton({label:l.Dialog.awsCredentialsError.buttons.enterKeysInTerminal})]});(await r.launch()).button.label===l.Dialog.awsCredentialsError.buttons.enterKeysInTerminal&&e.execute(u)})(r),new Error(n.statusText)}return await n.json()})().then((async e=>{j(!1),S(e)})).catch((e=>{y(e.message)})):j(!1)}),[a,h.model.inputFile]);const[_,S]=(0,n.useState)({}),[k,j]=(0,n.useState)(!0);return E?o().createElement("div",{className:X},E):k?null:a!==i.JobsView.CreateForm||(null==_?void 0:_.auto_detected_config)?o().createElement(m.Z,{theme:Jt()},o().createElement(p.StyledEngineProvider,{injectFirst:!0},o().createElement(Nt,{executionEnvironments:_,requestClient:e,contentsManager:t,jobsView:a,errors:c,handleErrorsChange:g,...h}))):null},At={id:"@amzn/sagemaker-scheduler:scheduler",autoStart:!1,requires:[a.ISettingRegistry],provides:i.Scheduler.IAdvancedOptions,activate:(e,t)=>r=>{const n=e.serviceManager.serverSettings,a=new b.ContentsManager;return o().createElement(f.StyledEngineProvider,{injectFirst:!0},o().createElement($e,{app:e},o().createElement(Dt,{requestClient:n,contentsManager:a,settingRegistry:t,commands:e.commands,...r})))}};var Vt;!function(e){e.eventDetail="eventDetail"}(Vt||(Vt={}));const Rt="NotebookJobs",Lt={"org.jupyter.jupyter-scheduler.notebook-header.create-job":`${Rt}-CreateJob-FromNotebookHeader`,"org.jupyter.jupyter-scheduler.file-browser.create-job":`${Rt}-CreateJob-FromFileBrowser`,"org.jupyter.jupyter-scheduler.launcher.show-jobs":`${Rt}-JobsList-OpenFromLauncher`,"org.jupyter.jupyter-scheduler.create-job.options.package_input_folder.check":`${Rt}-CreateJob-InputFolderCheck`,"org.jupyter.jupyter-scheduler.create-job.options.package_input_folder.uncheck":`${Rt}-CreateJob-InputFolderUncheck`,"org.jupyter.jupyter-scheduler.create-job.create-job":`${Rt}-CreateJob-Create`,"org.jupyter.jupyter-scheduler.create-job.cancel":`${Rt}-CreateJob-Cancel`,"org.jupyter.jupyter-scheduler.create-job.create-job.success":`${Rt}-CreateJob-Success`,"org.jupyter.jupyter-scheduler.create-job.create-job.failure":`${Rt}-CreateJob-Failure`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition":`${Rt}-CreateJob-CreateJobDefinition`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition.success":`${Rt}-CreateJobDefinition-Success`,"org.jupyter.jupyter-scheduler.create-job.create-job-definition.failure":`${Rt}-CreateJobDefinition-Failure`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job":`${Rt}-CreateJobFromDefinition-Create`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job.success":`${Rt}-CreateJobFromDefinition-Success`,"org.jupyter.jupyter-scheduler.create-job-from-definition.create-job.failure":`${Rt}-CreateJobFromDefinition-Failure`,"org.jupyter.jupyter-scheduler.create-job-from-definition.cancel":`${Rt}-CreateJobFromDefinition-Cancel`,"org.jupyter.jupyter-scheduler.create-job.job-type.run-now":`${Rt}-CreateJobType-RunNow`,"org.jupyter.jupyter-scheduler.create-job.job-type.run-on-schedule":`${Rt}-CreateJobType-RunOnSchedule`,"org.jupyter.jupyter-scheduler.create-job.advanced-options.expand":`${Rt}-CreateJob-ExpandAdvancedOptions`,"org.jupyter.jupyter-scheduler.create-job.advanced-options.collapse":`${Rt}-CreateJob-CollapseAdvancedOptions`,"org.jupyter.jupyter-scheduler.jobs-list.reload":`${Rt}-JobsList-Reload`,"org.jupyter.jupyter-scheduler.jobs-definition-list.reload":`${Rt}-JobsDefinitionList-Reload`,"org.jupyter.jupyter-scheduler.jobs-list.open-input-file":`${Rt}-JobsList-OpenInputFile`,"org.jupyter.jupyter-scheduler.jobs-list.open-output-file":`${Rt}-JobsList-OpenOutputFile`,"org.jupyter.jupyter-scheduler.job-list.stop-confirm":`${Rt}-JobsList-StopConfirm`,"org.jupyter.jupyter-scheduler.jobs-list.download":`${Rt}-JobsList-Download`,"org.jupyter.jupyter-scheduler.jobs-list.open-detail":`${Rt}-JobsList-OpenDetail`,"org.jupyter.jupyter-scheduler.jobs-list.delete":`${Rt}-JobsList-Delete`,"org.jupyter.jupyter-scheduler.jobs-list.stop":`${Rt}-JobsList-Stop`,"org.jupyter.jupyter-scheduler.job-definition-list.open-detail":`${Rt}-JobsDefinitionList-OpenDetail`,"org.jupyter.jupyter-scheduler.job-definition-list.pause":`${Rt}-JobsDefinitionList-Pause`,"org.jupyter.jupyter-scheduler.job-definition-list.resume":`${Rt}-JobsDefinitionList-Resume`,"org.jupyter.jupyter-scheduler.job-definition-list.delete":`${Rt}-JobsDefinitionList-Delete`,"org.jupyter.jupyter-scheduler.job-detail.open-input-file":`${Rt}-JobsDefinitionList-OpenInputFile`,"org.jupyter.jupyter-scheduler.job-detail.open-output-file":`${Rt}-JobsDefinitionList-OpenOutputFile`,"org.jupyter.jupyter-scheduler.job-detail.delete":`${Rt}-JobDetail-Delete`,"org.jupyter.jupyter-scheduler.job-detail.stop":`${Rt}-JobDetail-Stop`,"org.jupyter.jupyter-scheduler.job-detail.download":`${Rt}-JobDetail-Download`,"org.jupyter.jupyter-scheduler.job-detail.reload":`${Rt}-JobDetail-Reload`,"org.jupyter.jupyter-scheduler.job-definition-detail.reload":`${Rt}-JobDefinitonDetail-Reload`,"org.jupyter.jupyter-scheduler.job-definition-detail.run":`${Rt}-JobDefinitonDetail-Run`,"org.jupyter.jupyter-scheduler.job-definition-detail.pause":`${Rt}-JobDefinitonDetail-Pause`,"org.jupyter.jupyter-scheduler.job-definition-detail.resume":`${Rt}-JobDefinitonDetail-Resume`,"org.jupyter.jupyter-scheduler.job-definition-detail.edit":`${Rt}-JobDefinitonDetail-Edit`,"org.jupyter.jupyter-scheduler.job-definition-detail.delete":`${Rt}-JobDefinitonDetail-Delete`,"org.jupyter.jupyter-scheduler.job-definition-edit.save":`${Rt}-JobDefinitonDetail-Save`,"org.jupyter.jupyter-scheduler.job-definition-edit.cancel":`${Rt}-JobDefinitonEdit-Cancel`},$t=async e=>{var t;let r;const n=null!==(t=Lt[e.body.name])&&void 0!==t?t:e.body.name;r=e.body.detail?JSON.stringify({name:n,error:e.body.detail}):n,window&&window.panorama&&window.panorama("trackCustomEvent",{eventType:Vt.eventDetail,eventDetail:r,eventContext:Rt,timestamp:e.timestamp.getTime()})},zt=[At,{id:"@amzn/sagemaker-scheduler:schedulerTelemetry",autoStart:!0,provides:i.Scheduler.TelemetryHandler,activate:e=>$t}]}}]);