import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")
# openai.api_key = ""

prompt="""summarize action and failed reason from text

Text: 
failed to reconcile network error using unmanaged vpc and subnet <*> cidr specified but it doesn t exist in vpc <*> cluster <*> name <*> namespace <*> reconciler group <*> reconciler kind AWSCluster

action: 
error using unmanaged vpc and subnet
reason
cidr specified but it doesn t exist in vpc


Text: 
failed to reconcile LB attachment error could not register control plane instance <*> with load balancer failed to register instance with APIServer ELB <*> instance is in availability zone <*> no public subnets attached to the ELB in the same zone

action: 
could not register control plane instance with load balancer
reason:
no public subnets attached to the ELB in the same zone


Text:
Error deleting a network error googleapi Error <*> <*> <*> The network resource <*> is already being used by <*> namespace <*> reconciler group <*> reconciler kind GCPCluster name <*>

action:
Error deleting a network
reason:
The network resource is already being used


Text:
Subnetwork not found.. skipping error googleapi Error <*> The resource <*> was not found notFound namespace <*> reconciler group <*> reconciler kind GCPCluster name <*> region <*>

action:
Subnetwork not found
reason:
resource not found


Text:
Reconciler error error failed to retrieve Spec.ProviderID from infrastructure provider for Machine <*> in namespace <*> field not found name <*> namespace <*> reconciler group <*> reconciler kind Machine

action:
failed to retrieve Spec.ProviderID from infrastructure provider
reason:
field not found


Text:
Failed to update SpectroClusterStatusConditions Code ClusterOperationNotAllowed Msg cluster operation cluster conditionType update not allowed with cluster state Deleted Ref <*> Details <nil> cluster <*>

action:
Failed to update SpectroClusterStatusConditions
reason:
cluster conditionType update not allowed with cluster state Deleted

Text:
failed to list all ingress spectrocluster Namespace <*> Name <*> error detail Get https <*> <*> dial tcp lookup <*> on <*> <*> no such host

action:
failed to list all ingress
reason:
no such host

Text:
Reconciler error error kubeconfig not available name <*> namespace <*> reconciler group <*> reconciler kind SpectroCluster

action:
kubeconfig not available
reason:
kubeconfig not available

Text:
Reconciler error error error creating client and cache for remote cluster error creating <*> rest mapper for remote cluster <*> context deadline exceeded name <*> namespace <*> reconciler group <*> reconciler kind Machine

action:
error creating client and cache for remote cluster
reason:
context deadline exceeded

Text:
Reconciler error error failed to force pivot cluster <*> name <*> namespace <*> reconciler group <*> reconciler kind SpectroCluster

action:
failed to force pivot cluster
reason:
failed to force pivot cluster

Text:
error deleting network for AWSManagedControlPlane error error patching conditions The condition ClusterSecurityGroupsReady was modified by a different process and this caused a merge/ChangeCondition conflict <*> n tType ClusterSecurityGroupsReady n tStatus False n tSeverity Info <*> tLastTransitionTime <*> Time s <*> <*> <*> <*> <*> UTC n+ tLastTransitionTime <*> Time s <*> <*> <*> <*> <*> UTC <*> tReason Deleting n+ tReason Deleted n tMessage n n reconciler group <*> reconciler kind AWSManagedControlPlane name <*> namespace <*>

action:
error deleting network for AWSManagedControlPlane
reason:
The condition ClusterSecurityGroupsReady was modified by a different process and this caused a merge/ChangeCondition conflict

Text:
unable to parse crd file continue to next error couldn t get version/kind json parse error json cannot unmarshal array into Go value of type struct APIVersion string json apiVersion omitempty Kind string json kind omitempty spectrocluster Namespace <*> Name <*> failed file <*>

action:
unable to parse crd file continue to next
reason:
json cannot unmarshal array into Go value of type struct APIVersion string


Text:
Error removing protection finalizer from PVC err Operation cannot be fulfilled on persistentvolumeclaims <*> StorageError invalid object Code 4 Key <*> ResourceVersion 0 AdditionalErrorMsg Precondition failed UID in precondition <*> UID in object meta PVC <*>

action:
Error removing protection finalizer from PVC
reason:
Precondition failed UID in precondition


Text:
reconciler error error failed to delete security group <*> dependencyviolation resource <*> has a dependent object n tstatus code <*> request id <*> name varun-cluster namespace <*> reconciler group <*> reconciler kind awscluster
"""

response = openai.Completion.create(
  engine="davinci",
  prompt=prompt,
  temperature=0.5,
  max_tokens=120,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0,
  stop=["\n\n"]
)

print(response.choices[0].text)
