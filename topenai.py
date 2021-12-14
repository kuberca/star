import os
import openai

# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"

prompt="""summarize keywords from text

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
