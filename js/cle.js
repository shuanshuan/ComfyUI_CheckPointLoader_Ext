import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
app.registerExtension({ 
	name: "art.quanse.CheckpointLoaderExt",
	async setup() { 
		console.log("art.quanse.CheckpointLoaderExt, Setup complete!")
	},
    async beforeRegisterNodeDef(nodeType, nodeData, app){
        if (nodeType?.comfyClass=="CheckpointLoaderExt") { 
            const original_getExtraMenuOptions = nodeType.prototype.getExtraMenuOptions;
            nodeType.prototype.getExtraMenuOptions = function(_, options) {
                original_getExtraMenuOptions?.apply(this, arguments);
                options.push({
                    content: "Checkpoints Info Manager",
                    callback: async () => {
                        window.open('/art.quanse/web', '_blank');
                    }
                })
            }   
        }
    },

    async nodeCreated(node) {
        if (node?.comfyClass === "CheckpointLoaderExt") {

           

            let model = node.widgets[0];
            model.callback = function(){
                // console.log(model.value)
                fetchApi(model.value,node)
            }    
        }
    }
})



async function fetchApi(modelName,curNode) {
   let response = await api.fetchApi("/art.quanse/cp/info/"+modelName)
   let result= await response.json();
   console.log("result",result)
//    let prompt = await app.graphToPrompt()
//    console.log(prompt)
//    console.log(prompt.workflow.last_node_id)
//    let nodeString = `{"inputs":[{"name":"clip","type":"CLIP","link":null}],"size":{"0":315,"1":58},"widgets":[{"type":"number","name":"stop_at_clip_layer","value":-1,"options":{"min":-24,"max":-1,"step":10,"round":1,"precision":0}}],"outputs":[{"name":"CLIP","type":"CLIP","links":null,"shape":3}],"serialize_widgets":true,"IS_UE":false}`;
//    const node = await LiteGraph.createNode("CLIPSetLastLayer");
//    node.pos = [120,100]
//    node.widgets[0].value=-12;
//    app.graph.add(node);

   
    // console.log(prompt)
    handleClip(result,curNode)
    handleVae(result,curNode)
}
async function handleVae(result,curNode){
    if(!result){
        return;
    } 
    let vaeValue = result[4]
  
    if(!vaeValue){
        let node =  await LiteGraph.createNode("VAELoader");
        app.graph.add(node);
        node.pos = [curNode.pos[0]+curNode.size[0]+50, curNode.pos[1]+20]
    }
}
async function handleClip(result,curNode){
    if(!result){
        return;
    } 
    let skip = result[5]

    const link_id =curNode.outputs[1].links?.[0]
    let node=null;
    if(link_id){
        const LLink_object = app.graph.links[link_id]
        node =app.graph.getNodeById(LLink_object.target_id)
        if (node?.comfyClass === "CLIPSetLastLayer"){
            node.widgets[0].value=skip;
        }else{
            node==null;
        }
       
    }

    if(!node && skip!=0){
        node =  await LiteGraph.createNode("CLIPSetLastLayer");
        app.graph.add(node);
        node.widgets[0].value=skip;
        node.pos = [curNode.pos[0]+curNode.size[0]+50, curNode.pos[1]]
    }
}



