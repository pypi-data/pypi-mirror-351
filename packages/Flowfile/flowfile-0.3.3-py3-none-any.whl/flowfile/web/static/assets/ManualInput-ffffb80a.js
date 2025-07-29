import { N as NodeButton, a as NodeTitle } from "./nodeTitle-cad6fd9d.js";
import { r as ref, d as defineComponent, l as computed, m as watch, b as resolveComponent, c as openBlock, e as createElementBlock, f as createVNode, w as withCtx, p as createBaseVNode, F as Fragment, q as renderList, a5 as withDirectives, a6 as vModelText, g as createTextVNode, s as normalizeClass, t as toDisplayString, i as createCommentVNode, E as ElNotification, _ as _export_sfc, n as onMounted, R as nextTick, h as createBlock, a7 as Teleport } from "./index-f25c9283.js";
import { u as useNodeStore } from "./PopOver-3bdf8951.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-1d456350.js";
import "./designer-4736134f.js";
const createManualInput = (flowId = -1, nodeId = -1, pos_x = 0, pos_y = 0) => {
  const nodeManualInput = ref({
    flow_id: flowId,
    node_id: nodeId,
    pos_x,
    pos_y,
    cache_input: false,
    raw_data: [],
    cache_results: false
    // Add the missing property 'cache_results'
  });
  return nodeManualInput;
};
const _hoisted_1 = { key: 0 };
const _hoisted_2 = { class: "settings-section" };
const _hoisted_3 = { class: "table-container" };
const _hoisted_4 = { class: "modern-table" };
const _hoisted_5 = ["onClick"];
const _hoisted_6 = ["onUpdate:modelValue"];
const _hoisted_7 = ["onUpdate:modelValue"];
const _hoisted_8 = ["onClick"];
const _hoisted_9 = { class: "controls-section" };
const _hoisted_10 = { class: "button-group" };
const _hoisted_11 = {
  key: 0,
  class: "raw-data-section"
};
const _hoisted_12 = { class: "raw-data-controls" };
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "manualInput",
  props: {
    nodeId: {}
  },
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const dataLoaded = ref(false);
    const nodeManualInput = ref(null);
    const columns = ref([]);
    const rows = ref([]);
    const showRawData = ref(false);
    const rawDataString = ref("");
    let nextColumnId = 1;
    let nextRowId = 1;
    const rawData = computed(() => {
      return rows.value.map((row) => {
        const obj = {};
        for (const col of columns.value) {
          obj[col.name] = row.values[col.id];
        }
        return obj;
      });
    });
    const initializeEmptyTable = () => {
      rows.value = [{ id: 1, values: { 1: "" } }];
      columns.value = [{ id: 1, name: "Column 1" }];
      nextColumnId = 2;
      nextRowId = 2;
    };
    const populateTableFromData = (data) => {
      rows.value = [];
      columns.value = [];
      data.forEach((item, rowIndex) => {
        const row = { id: rowIndex + 1, values: {} };
        Object.keys(item).forEach((key, colIndex) => {
          if (rowIndex === 0) {
            columns.value.push({ id: colIndex + 1, name: key });
          }
          row.values[colIndex + 1] = item[key];
        });
        rows.value.push(row);
      });
      nextColumnId = columns.value.length + 1;
      nextRowId = rows.value.length + 1;
    };
    const loadNodeData = async (nodeId) => {
      const nodeResult = await nodeStore.getNodeData(nodeId, false);
      if (nodeResult == null ? void 0 : nodeResult.setting_input) {
        nodeManualInput.value = nodeResult.setting_input;
        if (nodeResult.setting_input.raw_data) {
          populateTableFromData(nodeResult.setting_input.raw_data);
        } else {
          initializeEmptyTable();
        }
      } else {
        nodeManualInput.value = createManualInput(nodeStore.flow_id, nodeStore.node_id).value;
        initializeEmptyTable();
      }
      rawDataString.value = JSON.stringify(rawData.value, null, 2);
      dataLoaded.value = true;
    };
    const addColumn = () => {
      columns.value.push({ id: nextColumnId, name: `Column ${nextColumnId}` });
      nextColumnId++;
    };
    const addRow = () => {
      const newRow = { id: nextRowId, values: {} };
      columns.value.forEach((col) => {
        newRow.values[col.id] = "";
      });
      rows.value.push(newRow);
      nextRowId++;
    };
    const deleteColumn = (id) => {
      const index = columns.value.findIndex((col) => col.id === id);
      if (index !== -1) {
        columns.value.splice(index, 1);
        rows.value.forEach((row) => {
          delete row.values[id];
        });
      }
    };
    const deleteRow = (id) => {
      const index = rows.value.findIndex((row) => row.id === id);
      if (index !== -1) {
        rows.value.splice(index, 1);
      }
    };
    const toggleRawData = () => {
      showRawData.value = !showRawData.value;
    };
    const updateTableFromRawData = () => {
      try {
        const newData = JSON.parse(rawDataString.value);
        if (!Array.isArray(newData)) {
          ElNotification({
            title: "Error",
            message: "Data must be an array of objects",
            type: "error"
          });
          return;
        }
        populateTableFromData(newData);
        ElNotification({
          title: "Success",
          message: "Table updated successfully",
          type: "success"
        });
      } catch (error) {
        ElNotification({
          title: "Error",
          message: "Invalid JSON format. Please check your input.",
          type: "error"
        });
      }
    };
    const pushNodeData = async () => {
      if (nodeManualInput.value) {
        nodeManualInput.value.raw_data = rawData.value;
        await nodeStore.updateSettings(nodeManualInput);
      }
      dataLoaded.value = false;
    };
    watch(rawData, (newVal) => {
      rawDataString.value = JSON.stringify(newVal, null, 2);
    });
    __expose({
      loadNodeData,
      pushNodeData
    });
    return (_ctx, _cache) => {
      const _component_el_button = resolveComponent("el-button");
      const _component_el_input = resolveComponent("el-input");
      const _component_el_collapse_transition = resolveComponent("el-collapse-transition");
      return dataLoaded.value && nodeManualInput.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeManualInput.value,
          "onUpdate:modelValue": _cache[1] || (_cache[1] = ($event) => nodeManualInput.value = $event)
        }, {
          default: withCtx(() => [
            createBaseVNode("div", _hoisted_2, [
              createBaseVNode("div", _hoisted_3, [
                createBaseVNode("table", _hoisted_4, [
                  createBaseVNode("thead", null, [
                    createBaseVNode("tr", null, [
                      (openBlock(true), createElementBlock(Fragment, null, renderList(columns.value, (col) => {
                        return openBlock(), createElementBlock("td", {
                          key: "delete-" + col.id
                        }, [
                          createBaseVNode("button", {
                            class: "delete-button",
                            onClick: ($event) => deleteColumn(col.id)
                          }, null, 8, _hoisted_5)
                        ]);
                      }), 128))
                    ]),
                    createBaseVNode("tr", null, [
                      (openBlock(true), createElementBlock(Fragment, null, renderList(columns.value, (col) => {
                        return openBlock(), createElementBlock("th", {
                          key: col.id
                        }, [
                          withDirectives(createBaseVNode("input", {
                            "onUpdate:modelValue": ($event) => col.name = $event,
                            class: "input-header",
                            type: "text"
                          }, null, 8, _hoisted_6), [
                            [vModelText, col.name]
                          ])
                        ]);
                      }), 128))
                    ])
                  ]),
                  createBaseVNode("tbody", null, [
                    (openBlock(true), createElementBlock(Fragment, null, renderList(rows.value, (row) => {
                      return openBlock(), createElementBlock("tr", {
                        key: row.id
                      }, [
                        (openBlock(true), createElementBlock(Fragment, null, renderList(columns.value, (col) => {
                          return openBlock(), createElementBlock("td", {
                            key: col.id
                          }, [
                            withDirectives(createBaseVNode("input", {
                              "onUpdate:modelValue": ($event) => row.values[col.id] = $event,
                              class: "input-cell",
                              type: "text"
                            }, null, 8, _hoisted_7), [
                              [vModelText, row.values[col.id]]
                            ])
                          ]);
                        }), 128)),
                        createBaseVNode("td", null, [
                          createBaseVNode("button", {
                            class: "delete-button",
                            onClick: ($event) => deleteRow(row.id)
                          }, null, 8, _hoisted_8)
                        ])
                      ]);
                    }), 128))
                  ])
                ])
              ]),
              createBaseVNode("div", _hoisted_9, [
                createBaseVNode("div", _hoisted_10, [
                  createVNode(_component_el_button, {
                    type: "primary",
                    size: "small",
                    onClick: addColumn
                  }, {
                    icon: withCtx(() => _cache[2] || (_cache[2] = [
                      createBaseVNode("i", { class: "fas fa-plus" }, null, -1)
                    ])),
                    default: withCtx(() => [
                      _cache[3] || (_cache[3] = createTextVNode(" Add Column "))
                    ]),
                    _: 1,
                    __: [3]
                  }),
                  createVNode(_component_el_button, {
                    type: "primary",
                    size: "small",
                    onClick: addRow
                  }, {
                    icon: withCtx(() => _cache[4] || (_cache[4] = [
                      createBaseVNode("i", { class: "fas fa-plus" }, null, -1)
                    ])),
                    default: withCtx(() => [
                      _cache[5] || (_cache[5] = createTextVNode(" Add Row "))
                    ]),
                    _: 1,
                    __: [5]
                  }),
                  createVNode(_component_el_button, {
                    type: "primary",
                    size: "small",
                    onClick: toggleRawData
                  }, {
                    icon: withCtx(() => [
                      createBaseVNode("i", {
                        class: normalizeClass(showRawData.value ? "fas fa-eye-slash" : "fas fa-eye")
                      }, null, 2)
                    ]),
                    default: withCtx(() => [
                      createTextVNode(" " + toDisplayString(showRawData.value ? "Hide" : "Show") + " Raw Data ", 1)
                    ]),
                    _: 1
                  })
                ])
              ]),
              createVNode(_component_el_collapse_transition, null, {
                default: withCtx(() => [
                  showRawData.value ? (openBlock(), createElementBlock("div", _hoisted_11, [
                    createVNode(_component_el_input, {
                      modelValue: rawDataString.value,
                      "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => rawDataString.value = $event),
                      type: "textarea",
                      rows: 8,
                      placeholder: JSON.stringify({ column1: "value1" }, null, 2)
                    }, null, 8, ["modelValue", "placeholder"]),
                    createBaseVNode("div", _hoisted_12, [
                      createVNode(_component_el_button, {
                        type: "primary",
                        size: "small",
                        onClick: updateTableFromRawData
                      }, {
                        default: withCtx(() => _cache[6] || (_cache[6] = [
                          createTextVNode(" Update Table ")
                        ])),
                        _: 1,
                        __: [6]
                      })
                    ])
                  ])) : createCommentVNode("", true)
                ]),
                _: 1
              })
            ])
          ]),
          _: 1
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const manualInput_vue_vue_type_style_index_0_scoped_5c4222c9_lang = "";
const manualInput = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-5c4222c9"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "ManualInput",
  props: {
    nodeId: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    const nodeStore = useNodeStore();
    const nodeButton = ref(null);
    const childComp = ref(null);
    const props = __props;
    const el = ref(null);
    const drawer = ref(false);
    const closeOnDrawer = () => {
      var _a;
      drawer.value = false;
      (_a = childComp.value) == null ? void 0 : _a.pushNodeData();
      nodeStore.isDrawerOpen = false;
    };
    const openDrawer = async () => {
      if (nodeStore.node_id === props.nodeId) {
        return;
      }
      nodeStore.closeDrawer();
      drawer.value = true;
      const drawerOpen = nodeStore.isDrawerOpen;
      nodeStore.isDrawerOpen = true;
      await nextTick();
      if (nodeStore.node_id === props.nodeId && drawerOpen) {
        return;
      }
      if (childComp.value) {
        childComp.value.loadNodeData(props.nodeId);
        nodeStore.openDrawer(closeOnDrawer);
      }
    };
    onMounted(async () => {
      await nextTick();
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", {
        ref_key: "el",
        ref: el
      }, [
        createVNode(NodeButton, {
          ref_key: "nodeButton",
          ref: nodeButton,
          "node-id": __props.nodeId,
          "image-src": "manual_input.png",
          title: `${__props.nodeId}: Manual input`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "Provide manual input",
            intro: "Provide a fixed data that can be used and combined with other tables."
          }),
          createVNode(manualInput, {
            ref_key: "childComp",
            ref: childComp,
            "node-id": __props.nodeId
          }, null, 8, ["node-id"])
        ])) : createCommentVNode("", true)
      ], 512);
    };
  }
});
export {
  _sfc_main as default
};
