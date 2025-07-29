import { r as ref, j as defineStore, a as axios, d as defineComponent, ae as useCssVars, n as onMounted, c as openBlock, e as createElementBlock, p as createBaseVNode, L as renderSlot, h as createBlock, t as toDisplayString, i as createCommentVNode, T as normalizeStyle, s as normalizeClass, a7 as Teleport, R as nextTick, _ as _export_sfc } from "./index-f25c9283.js";
const FLOW_ID_STORAGE_KEY = "last_flow_id";
ref(null);
const getDownstreamNodeIds = async (flow_id, node_id) => {
  const response = await axios.get("/node/downstream_node_ids", {
    params: { flow_id, node_id },
    headers: { accept: "application/json" }
  });
  return response.data;
};
const loadDownstreamNodeIds = async (flowId, nodeId) => {
  const downstreamNodeIds = await getDownstreamNodeIds(flowId, nodeId);
  return downstreamNodeIds;
};
const useNodeStore = defineStore("node", {
  state: () => {
    const savedFlowId = sessionStorage.getItem(FLOW_ID_STORAGE_KEY);
    const initialFlowId = savedFlowId ? parseInt(savedFlowId) : -1;
    return {
      inputCode: "",
      flow_id: initialFlowId,
      node_id: -1,
      previous_node_id: -1,
      nodeValidateFuncs: /* @__PURE__ */ new Map(),
      nodeData: null,
      node_exists: false,
      is_loaded: false,
      size_data_preview: 300,
      dataTypes: ["String", "Datetime", "Int64", "Int32", "Int16", "Float64", "Float32", "Boolean"],
      isDrawerOpen: false,
      isAnalysisOpen: false,
      drawCloseFunction: null,
      initialEditorData: "",
      runResults: {},
      nodeDescriptions: {},
      runNodeResults: {},
      runNodeValidations: {},
      currentRunResult: null,
      isRunning: false,
      showFlowResult: false,
      tableVisible: false,
      resultVersion: 0,
      vueFlowInstance: null,
      allExpressions: null,
      isShowingLogViewer: false,
      isStreamingLogs: false,
      displayLogViewer: true
    };
  },
  actions: {
    initializeResultCache(flowId) {
      if (!this.runNodeResults[flowId]) {
        this.runNodeResults[flowId] = {};
      }
    },
    initializeValidationCache(flowId) {
      if (!this.runNodeValidations[flowId]) {
        this.runNodeValidations[flowId] = {};
      }
    },
    setNodeResult(nodeId, result) {
      this.initializeResultCache(this.flow_id);
      this.runNodeResults[this.flow_id][nodeId] = result;
    },
    getNodeResult(nodeId) {
      var _a;
      return (_a = this.runNodeResults[this.flow_id]) == null ? void 0 : _a[nodeId];
    },
    resetNodeResult() {
      console.log("Clearing node results");
      this.runNodeResults = {};
    },
    clearFlowResults(flowId) {
      if (this.runNodeResults[flowId]) {
        delete this.runNodeResults[flowId];
      }
    },
    setNodeValidation(nodeId, nodeValidationInput) {
      if (typeof nodeId === "string") {
        nodeId = parseInt(nodeId);
      }
      this.initializeValidationCache(this.flow_id);
      const nodeValidation = {
        ...nodeValidationInput,
        validationTime: Date.now() / 1e3
      };
      this.runNodeValidations[this.flow_id][nodeId] = nodeValidation;
    },
    resetNodeValidation() {
      this.runNodeValidations = {};
    },
    getNodeValidation(nodeId) {
      var _a;
      return ((_a = this.runNodeValidations[this.flow_id]) == null ? void 0 : _a[nodeId]) || {
        isValid: true,
        error: "",
        validationTime: 0
      };
    },
    insertRunResult(runResult, showResult = true) {
      this.currentRunResult = runResult;
      this.runResults[runResult.flow_id] = runResult;
      this.showFlowResult = showResult;
      this.isShowingLogViewer = this.displayLogViewer && showResult;
      this.initializeResultCache(runResult.flow_id);
      runResult.node_step_result.forEach((nodeResult) => {
        this.runNodeResults[runResult.flow_id][nodeResult.node_id] = nodeResult;
      });
      this.resultVersion++;
    },
    resetRunResults() {
      this.runNodeResults = {};
      this.runResults = {};
      this.currentRunResult = null;
    },
    initializeDescriptionCache(flowId) {
      if (!this.nodeDescriptions[flowId]) {
        this.nodeDescriptions[flowId] = {};
      }
    },
    setNodeValidateFunc(nodeId, func) {
      if (typeof nodeId === "string") {
        nodeId = parseInt(nodeId);
      }
      this.nodeValidateFuncs.set(nodeId, func);
    },
    async validateNode(nodeId) {
      if (typeof nodeId === "string") {
        nodeId = parseInt(nodeId);
      }
      const func = this.nodeValidateFuncs.get(nodeId);
      if (func) {
        func();
      } else {
        console.warn("No validation function found for node", nodeId);
      }
    },
    setFlowId(flowId) {
      this.flow_id = flowId;
      try {
        sessionStorage.setItem(FLOW_ID_STORAGE_KEY, flowId.toString());
      } catch (error) {
        console.warn("Failed to store flow ID in session storage:", error);
      }
    },
    setVueFlowInstance(vueFlowInstance) {
      this.vueFlowInstance = vueFlowInstance;
    },
    setInitialEditorData(editorDataString) {
      this.initialEditorData = editorDataString;
    },
    getInitialEditorData() {
      return this.initialEditorData;
    },
    cacheNodeDescriptionDict(flowId, nodeId, description) {
      this.initializeDescriptionCache(flowId);
      this.nodeDescriptions[flowId][nodeId] = description;
    },
    clearNodeDescriptionCache(flowId, nodeId) {
      if (this.nodeDescriptions[flowId] && this.nodeDescriptions[flowId][nodeId]) {
        delete this.nodeDescriptions[flowId][nodeId];
      }
    },
    clearFlowDescriptionCache(flowId) {
      if (this.nodeDescriptions[flowId]) {
        delete this.nodeDescriptions[flowId];
      }
    },
    clearAllDescriptionCaches() {
      this.nodeDescriptions = {};
    },
    async getNodeDescription(nodeId, forceRefresh = false) {
      var _a, _b;
      this.initializeDescriptionCache(this.flow_id);
      if (!forceRefresh && ((_a = this.nodeDescriptions[this.flow_id]) == null ? void 0 : _a[nodeId])) {
        return this.nodeDescriptions[this.flow_id][nodeId];
      }
      try {
        const response = await axios.get("/node/description", {
          params: {
            node_id: nodeId,
            flow_id: this.flow_id
          }
        });
        this.cacheNodeDescriptionDict(this.flow_id, nodeId, response.data);
        return response.data;
      } catch (error) {
        console.info("Error fetching node description:", error);
        if ((_b = this.nodeDescriptions[this.flow_id]) == null ? void 0 : _b[nodeId]) {
          console.warn("Using cached description due to API error");
          return this.nodeDescriptions[this.flow_id][nodeId];
        }
        return "";
      }
    },
    async setNodeDescription(nodeId, description) {
      try {
        this.cacheNodeDescriptionDict(this.flow_id, nodeId, description);
        const response = await axios.post("/node/description/", JSON.stringify(description), {
          params: {
            flow_id: this.flow_id,
            node_id: nodeId
          },
          headers: {
            "Content-Type": "application/json"
          }
        });
        if (response.data.status === "success") {
          console.log(response.data.message);
        } else {
          console.warn("Unexpected success response structure:", response.data);
        }
      } catch (error) {
        if (error.response) {
          console.error("API error:", error.response.data.message);
        } else if (error.request) {
          console.error("The request was made but no response was received");
        } else {
          console.error("Error", error.message);
        }
        throw error;
      }
    },
    setCloseFunction(f) {
      this.drawCloseFunction = f;
    },
    getSizeDataPreview() {
      return this.size_data_preview;
    },
    setSizeDataPreview(newHeight) {
      this.size_data_preview = newHeight;
    },
    toggleDrawer() {
      console.log("toggleDrawer in column-store.ts");
      if (this.isDrawerOpen && this.drawCloseFunction) {
        this.pushNodeData();
      }
      this.isDrawerOpen = !this.isDrawerOpen;
    },
    pushNodeData() {
      if (this.drawCloseFunction && !this.isRunning) {
        this.drawCloseFunction();
        this.drawCloseFunction = null;
      }
    },
    openDrawer(close_function) {
      console.log("openDrawer in column-store.ts");
      if (this.isDrawerOpen) {
        console.log("pushing data");
        this.pushNodeData();
      }
      if (close_function) {
        this.drawCloseFunction = close_function;
      }
      this.isDrawerOpen = true;
    },
    closeDrawer() {
      this.isDrawerOpen = false;
      if (this.drawCloseFunction) {
        this.pushNodeData();
      }
      this.node_id = -1;
    },
    openAnalysisDrawer(close_function) {
      console.log("openAnalysisDrawer in column-store.ts");
      if (this.isAnalysisOpen) {
        this.pushNodeData();
      }
      if (close_function) {
        this.drawCloseFunction = close_function;
      }
      this.isAnalysisOpen = true;
    },
    closeAnalysisDrawer() {
      this.isAnalysisOpen = false;
      if (this.drawCloseFunction) {
        console.log("closeDrawer in column-store.ts");
        this.pushNodeData();
      }
    },
    getDataTypes() {
      return this.dataTypes;
    },
    setInputCode(newCode) {
      this.inputCode = newCode;
    },
    showLogViewer() {
      console.log("triggered show log viewer");
      this.isShowingLogViewer = this.displayLogViewer;
    },
    hideLogViewer() {
      this.isShowingLogViewer = false;
    },
    toggleLogViewer() {
      console.log("triggered toggle log viewer");
      this.isShowingLogViewer = !this.isShowingLogViewer;
    },
    getRunResult(flow_id) {
      return this.runResults[flow_id] || null;
    },
    async getTableExample(flow_id, node_id) {
      try {
        const response = await axios.get("/node/data", {
          params: { flow_id, node_id },
          headers: { accept: "application/json" }
        });
        return response.data;
      } catch (error) {
        console.error("Error fetching table example:", error);
        return null;
      }
    },
    async getNodeData(node_id, useCache = true) {
      if (this.node_id === node_id && useCache) {
        if (this.nodeData) {
          this.is_loaded = true;
          return this.nodeData;
        }
      }
      try {
        this.setFlowIdAndNodeId(this.flow_id, node_id);
        const response = await axios.get("/node", {
          params: { flow_id: this.flow_id, node_id: this.node_id },
          headers: { accept: "application/json" }
        });
        this.nodeData = response.data;
        this.is_loaded = true;
        this.node_exists = true;
        return this.nodeData;
      } catch (error) {
        console.error("Error fetching node data:", error);
        this.nodeData = null;
        this.is_loaded = false;
        this.node_exists = false;
        return null;
      }
    },
    async reloadCurrentNodeData() {
      return this.getNodeData(this.node_id, false);
    },
    setFlowIdAndNodeId(flow_id, node_id) {
      if (this.node_id === node_id && this.flow_id === flow_id) {
        return;
      }
      console.log("Automatically pushing the node data ");
      this.pushNodeData();
      this.previous_node_id = this.node_id;
      if (this.flow_id !== flow_id) {
        this.setFlowId(flow_id);
      }
      this.node_id = node_id;
    },
    getCurrentNodeData() {
      return this.nodeData;
    },
    doReset() {
      this.is_loaded = false;
    },
    getVueFlowInstance() {
      return this.vueFlowInstance;
    },
    getEditorNodeData() {
      var _a;
      if (this.node_id) {
        return (_a = this.vueFlowInstance) == null ? void 0 : _a.findNode(String(this.node_id));
      }
      return null;
    },
    async fetchExpressionsOverview() {
      try {
        const response = await axios.get("/editor/expression_doc");
        this.allExpressions = response.data;
        return this.allExpressions;
      } catch (error) {
        console.error("Error fetching expressions overview:", error);
        return [];
      }
    },
    async getExpressionsOverview() {
      if (this.allExpressions) {
        return this.allExpressions;
      } else {
        return await this.fetchExpressionsOverview();
      }
    },
    async updateSettingsDirectly(inputData) {
      var _a, _b;
      try {
        const node = (_a = this.vueFlowInstance) == null ? void 0 : _a.findNode(String(this.node_id));
        inputData.pos_x = node.position.x;
        inputData.pos_y = node.position.y;
        console.log("updating settings");
        console.log("node", node);
        const response = await axios.post("/update_settings/", inputData, {
          params: {
            node_type: node.data.component.__name
          }
        });
        const downstreamNodeIds = await loadDownstreamNodeIds(this.flow_id, inputData.node_id);
        downstreamNodeIds.map((nodeId) => {
          this.validateNode(nodeId);
        });
        return response.data;
      } catch (error) {
        console.error("Error updating settings:", (_b = error.response) == null ? void 0 : _b.data);
        throw error;
      }
    },
    async updateSettings(inputData) {
      var _a, _b;
      try {
        const node = (_a = this.vueFlowInstance) == null ? void 0 : _a.findNode(String(this.node_id));
        inputData.value.pos_x = node.position.x;
        inputData.value.pos_y = node.position.y;
        console.log("updating settings");
        console.log("node", node);
        const response = await axios.post("/update_settings/", inputData.value, {
          params: {
            node_type: node.data.component.__name
          }
        });
        const downstreamNodeIds = await loadDownstreamNodeIds(
          this.flow_id,
          inputData.value.node_id
        );
        downstreamNodeIds.map((nodeId) => {
          this.validateNode(nodeId);
        });
        return response.data;
      } catch (error) {
        console.error("Error updating settings:", (_b = error.response) == null ? void 0 : _b.data);
        throw error;
      }
    },
    updateNodeDescription(nodeId, description) {
      this.cacheNodeDescriptionDict(this.flow_id, nodeId, description);
    }
  }
});
const _hoisted_1 = { class: "popover-container" };
const _hoisted_2 = { key: 0 };
const _hoisted_3 = ["innerHTML"];
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "PopOver",
  props: {
    content: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: ""
    },
    placement: {
      type: String,
      default: "top"
    },
    minWidth: {
      type: Number,
      default: 100
    },
    zIndex: {
      type: Number,
      default: 9999
    }
  },
  setup(__props) {
    useCssVars((_ctx) => ({
      "64450ce2": props.minWidth + "px"
    }));
    const visible = ref(false);
    const referenceEl = ref(null);
    const popoverEl = ref(null);
    const props = __props;
    const popoverStyle = ref({
      top: "0px",
      left: "0px",
      zIndex: props.zIndex.toString()
    });
    const showPopover = () => {
      visible.value = true;
      nextTick(() => {
        updatePosition();
      });
    };
    const hidePopover = () => {
      visible.value = false;
    };
    const updatePosition = () => {
      if (!referenceEl.value || !popoverEl.value)
        return;
      const referenceRect = referenceEl.value.getBoundingClientRect();
      const popoverRect = popoverEl.value.getBoundingClientRect();
      const offset = 20;
      let top = 0;
      let left = 0;
      switch (props.placement) {
        case "top":
          top = referenceRect.top - popoverRect.height - offset;
          left = referenceRect.left + referenceRect.width / 2 - popoverRect.width / 2;
          break;
        case "bottom":
          top = referenceRect.bottom + offset;
          left = referenceRect.left + referenceRect.width / 2 - popoverRect.width / 2;
          break;
        case "left":
          top = referenceRect.top + referenceRect.height / 2 - popoverRect.height / 2;
          left = referenceRect.left - popoverRect.width - offset;
          break;
        case "right":
          top = referenceRect.top + referenceRect.height / 2 - popoverRect.height / 2;
          left = referenceRect.right + offset;
          break;
      }
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      if (left < 10)
        left = 10;
      if (left + popoverRect.width > viewportWidth - 10) {
        left = viewportWidth - popoverRect.width - 10;
      }
      if (top < 10)
        top = 10;
      if (top + popoverRect.height > viewportHeight - 10) {
        top = viewportHeight - popoverRect.height - 10;
      }
      popoverStyle.value = {
        top: `${top}px`,
        left: `${left}px`,
        zIndex: props.zIndex.toString()
      };
    };
    onMounted(() => {
      window.addEventListener("resize", () => {
        if (visible.value) {
          updatePosition();
        }
      });
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1, [
        createBaseVNode("div", {
          ref_key: "referenceEl",
          ref: referenceEl,
          class: "popover-reference",
          onMouseenter: showPopover,
          onMouseleave: hidePopover
        }, [
          renderSlot(_ctx.$slots, "default", {}, void 0, true)
        ], 544),
        visible.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "body"
        }, [
          createBaseVNode("div", {
            ref_key: "popoverEl",
            ref: popoverEl,
            style: normalizeStyle(popoverStyle.value),
            class: normalizeClass(["popover", { "popover--left": props.placement === "left" }])
          }, [
            props.title !== "" ? (openBlock(), createElementBlock("h3", _hoisted_2, toDisplayString(props.title), 1)) : createCommentVNode("", true),
            createBaseVNode("p", {
              class: "content",
              innerHTML: props.content
            }, null, 8, _hoisted_3)
          ], 6)
        ])) : createCommentVNode("", true)
      ]);
    };
  }
});
const PopOver_vue_vue_type_style_index_0_scoped_e6f071d2_lang = "";
const PopOver = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-e6f071d2"]]);
export {
  PopOver as P,
  useNodeStore as u
};
