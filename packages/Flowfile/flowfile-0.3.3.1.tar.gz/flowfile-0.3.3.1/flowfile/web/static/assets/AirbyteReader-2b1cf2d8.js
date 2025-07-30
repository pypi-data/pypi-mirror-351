import { a as axios, d as defineComponent, r as ref, n as onMounted, l as computed, c as openBlock, e as createElementBlock, p as createBaseVNode, F as Fragment, q as renderList, g as createTextVNode, t as toDisplayString, i as createCommentVNode, a5 as withDirectives, a6 as vModelText, x as withKeys, f as createVNode, ag as vModelDynamic, s as normalizeClass, T as normalizeStyle, _ as _export_sfc, b as resolveComponent, w as withCtx, h as createBlock, u as unref, R as nextTick, a7 as Teleport } from "./index-f25c9283.js";
import { D as DropDownGeneric } from "./dropDownGeneric-1f4e32ec.js";
import { u as useNodeStore } from "./PopOver-3bdf8951.js";
import { C as CodeLoader } from "./vue-content-loader.es-860c0380.js";
import { G as GenericNodeSettings } from "./genericNodeSettings-1d456350.js";
import { N as NodeButton, a as NodeTitle } from "./nodeTitle-cad6fd9d.js";
import "./dropDown-d5a4014c.js";
import "./designer-4736134f.js";
const _imports_0 = "/images/airbyte.png";
const getAirbyteConnectors = async () => {
  const response = await axios.get(`/airbyte/available_connectors`);
  return response.data;
};
const getAirbyteConnectorTemplate = async (connector_name) => {
  const response = await axios.get(`/airbyte/config_template?connector_name=${connector_name}`);
  return response.data;
};
const getAirbyteAvailableConfigs = async () => {
  const response = await axios.get(`/airbyte/available_configs`);
  return response.data;
};
const setAirbyteConfigGetStreams = async (data) => {
  await axios.post(`/airbyte/set_airbyte_configs_for_streams`, data);
};
const processProperties = (properties) => {
  return Object.entries(properties).map(([propKey, propValue]) => ({
    key: propKey,
    type: propValue.type,
    description: propValue.description ?? "",
    title: propValue.title ?? "",
    airbyte_secret: propValue.airbyte_secret || false,
    input_value: propValue.default || null,
    default: propValue.default || null
  }));
};
const computeSchema = (schema) => {
  const entries = Object.entries(schema.properties);
  const localParsedConfig = entries.map(([key, value]) => {
    var _a;
    const isRequired = ((_a = schema.required) == null ? void 0 : _a.includes(key)) || false;
    const baseField = {
      title: value.title,
      type: value.type,
      key,
      required: isRequired,
      description: value.description,
      isOpen: false,
      airbyte_secret: value.airbyte_secret || false,
      input_value: value.default || null,
      default: value.default || null,
      properties: []
    };
    if ("oneOf" in value && Array.isArray(value.oneOf)) {
      return {
        ...baseField,
        oneOf: value.oneOf.map((option) => {
          const mappedProperties = option.properties ? Object.entries(option.properties).reduce(
            (acc, [propKey, propValue]) => {
              if (propKey === "auth_type") {
                acc[propKey] = {
                  type: propValue.type,
                  const: propValue.const,
                  input_value: propValue.const,
                  default: propValue.const
                };
              } else {
                acc[propKey] = {
                  title: propValue.title,
                  type: propValue.type,
                  description: propValue.description,
                  airbyte_secret: propValue.airbyte_secret,
                  input_value: propValue.default || null,
                  default: propValue.default
                };
              }
              return acc;
            },
            {}
          ) : {};
          return {
            title: option.title,
            type: option.type,
            description: option.description,
            required: option.required || [],
            properties: mappedProperties
          };
        }),
        selectedOption: void 0
      };
    } else if (value.properties) {
      return {
        ...baseField,
        properties: processProperties(value.properties)
      };
    } else {
      return baseField;
    }
  });
  return localParsedConfig;
};
const processPropertyValue = (value, type) => {
  if (value === null || value === void 0 || value === "") {
    return null;
  }
  if (type === "integer" || type === "number") {
    return typeof value === "string" ? Number(value) : value;
  }
  if (type === "array" && Array.isArray(value)) {
    return value;
  }
  if (type === "string" && typeof value === "string") {
    try {
      JSON.parse(value);
      return value;
    } catch {
      if (value.includes("{") && value.includes("}")) {
        try {
          const parsed = JSON.parse(value.replace(/\s+/g, " "));
          return JSON.stringify(parsed, null, 2);
        } catch {
          return value.trim();
        }
      }
      return value;
    }
  }
  return value;
};
const getConfigSettings = (parsedConfig) => {
  const result = {};
  parsedConfig.forEach((item) => {
    if (item.oneOf && Array.isArray(item.oneOf) && item.selectedOption !== void 0 && item.selectedOption < item.oneOf.length) {
      const selectedOption = item.oneOf[item.selectedOption];
      if (!(selectedOption == null ? void 0 : selectedOption.properties)) {
        return;
      }
      if (item.input_value) {
        result[item.key] = {};
        Object.entries(item.input_value).forEach(([key, value]) => {
          var _a, _b;
          const processedValue = processPropertyValue(
            value,
            ((_b = (_a = selectedOption.properties) == null ? void 0 : _a[key]) == null ? void 0 : _b.type) ?? "string"
          );
          if (processedValue !== null) {
            result[item.key][key] = processedValue;
          }
        });
      }
    } else if (item.properties && item.properties.length > 0) {
      result[item.key] = {};
      item.properties.forEach((property) => {
        const value = processPropertyValue(property.input_value, property.type);
        if (value !== null) {
          result[item.key][property.key] = value;
        } else if (property.default !== null) {
          result[item.key][property.key] = property.default;
        }
      });
    } else if (item.input_value !== null && item.input_value !== "") {
      const value = processPropertyValue(item.input_value, item.type);
      if (value !== null) {
        result[item.key] = value;
      }
    } else if (item.default !== null) {
      result[item.key] = item.default;
    }
  });
  return result;
};
const _hoisted_1$1 = { class: "form-container" };
const _hoisted_2$1 = { class: "form-grid" };
const _hoisted_3$1 = {
  key: 0,
  class: "single-item"
};
const _hoisted_4$1 = ["onMouseover"];
const _hoisted_5$1 = {
  key: 0,
  class: "tag"
};
const _hoisted_6$1 = { class: "array-input-section" };
const _hoisted_7$1 = { class: "input-with-button" };
const _hoisted_8$1 = ["onUpdate:modelValue", "placeholder", "onKeyup"];
const _hoisted_9$1 = ["onClick"];
const _hoisted_10$1 = { class: "items-container" };
const _hoisted_11$1 = ["onClick"];
const _hoisted_12$1 = {
  key: 1,
  class: "collapsible-section"
};
const _hoisted_13$1 = ["onMouseover"];
const _hoisted_14$1 = {
  key: 0,
  class: "tag"
};
const _hoisted_15 = {
  key: 0,
  class: "nested-content"
};
const _hoisted_16 = ["onMouseover"];
const _hoisted_17 = {
  key: 0,
  class: "tag"
};
const _hoisted_18 = ["onUpdate:modelValue", "type", "placeholder"];
const _hoisted_19 = {
  key: 2,
  class: "single-item"
};
const _hoisted_20 = ["onMouseover"];
const _hoisted_21 = {
  key: 0,
  class: "tag"
};
const _hoisted_22 = ["onUpdate:modelValue", "type", "placeholder"];
const _hoisted_23 = {
  key: 3,
  class: "collapsible-section"
};
const _hoisted_24 = ["onClick"];
const _hoisted_25 = { class: "minimal-chevron" };
const _hoisted_26 = {
  key: 0,
  class: "tag"
};
const _hoisted_27 = {
  key: 0,
  class: "nested-content"
};
const _hoisted_28 = ["onMouseover"];
const _hoisted_29 = {
  key: 0,
  class: "tag"
};
const _hoisted_30 = ["onUpdate:modelValue", "type", "placeholder"];
const _sfc_main$2 = /* @__PURE__ */ defineComponent({
  __name: "airbyteConfigForm",
  props: {
    parsedConfig: {}
  },
  setup(__props, { expose: __expose }) {
    const props = __props;
    const popover = ref({
      show: false,
      content: "",
      x: 0,
      y: 0
    });
    const localConfig = ref([...props.parsedConfig]);
    const selectedValues = ref(new Array(props.parsedConfig.length).fill(""));
    const newArrayValue = ref({});
    function isStringArray(value) {
      return Array.isArray(value) && value.every((item) => typeof item === "string");
    }
    const getArrayValues = (item) => {
      if (!item.input_value) {
        item.input_value = [];
      }
      if (!isStringArray(item.input_value)) {
        item.input_value = [];
      }
      return item.input_value;
    };
    const addArrayValue = (item) => {
      const value = newArrayValue.value[item.key];
      if (!(value == null ? void 0 : value.trim()))
        return;
      if (!item.input_value || !isStringArray(item.input_value)) {
        item.input_value = [];
      }
      const currentArray = item.input_value;
      if (!currentArray.includes(value)) {
        currentArray.push(value);
        newArrayValue.value[item.key] = "";
      }
    };
    const removeArrayValue = (item, index) => {
      if (isStringArray(item.input_value)) {
        item.input_value.splice(index, 1);
      }
    };
    onMounted(() => {
      props.parsedConfig.forEach((item, index) => {
        if (item.oneOf && typeof item.selectedOption === "number" && item.selectedOption >= 0) {
          selectedValues.value[index] = item.oneOf[item.selectedOption].title;
        }
      });
    });
    const showPopover = (content, event) => {
      if (!content)
        return;
      popover.value = {
        show: true,
        content,
        x: event.clientX + 10,
        y: event.clientY + 10
      };
    };
    const hidePopover = () => {
      popover.value.show = false;
    };
    const toggle = (index) => {
      localConfig.value[index].isOpen = !localConfig.value[index].isOpen;
    };
    const isRequired = (schema, fieldName) => {
      var _a;
      return ((_a = schema.required) == null ? void 0 : _a.includes(fieldName)) || false;
    };
    const updateSelectedOption = (item, selectedValue, index) => {
      if (!item.oneOf)
        return;
      const optionIndex = item.oneOf.findIndex((opt) => opt.title === selectedValue);
      if (optionIndex === -1)
        return;
      selectedValues.value[index] = selectedValue;
      const localItem = localConfig.value[index];
      if (!localItem || !localItem.oneOf)
        return;
      localItem.selectedOption = optionIndex;
      const selectedOption = localItem.oneOf[optionIndex];
      const previousValue = localItem.input_value;
      const newInputValue = {};
      if (selectedOption.properties) {
        Object.entries(selectedOption.properties).forEach(([key, prop]) => {
          if (key === "auth_type") {
            newInputValue[key] = prop.const;
          } else if (previousValue && typeof previousValue === "object" && key in previousValue) {
            newInputValue[key] = previousValue[key];
          } else {
            newInputValue[key] = prop.input_value ?? prop.default ?? "";
          }
        });
      }
      localItem.input_value = newInputValue;
    };
    const computedSchema = computed(() => {
      return props.parsedConfig.map((item) => {
        if (item.oneOf) {
          return {
            ...item,
            selectedOption: item.selectedOption,
            oneOf: item.oneOf.map((option) => ({
              ...option,
              properties: option.properties ? Object.entries(option.properties).reduce(
                (acc, [key, value]) => {
                  acc[key] = { ...value };
                  return acc;
                },
                {}
              ) : {}
            }))
          };
        }
        return item;
      });
    });
    __expose({
      localConfig
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", _hoisted_1$1, [
        createBaseVNode("div", _hoisted_2$1, [
          (openBlock(true), createElementBlock(Fragment, null, renderList(computedSchema.value, (item, index) => {
            return openBlock(), createElementBlock("div", {
              key: index,
              class: "form-item-wrapper"
            }, [
              item.type === "array" ? (openBlock(), createElementBlock("div", _hoisted_3$1, [
                createBaseVNode("div", {
                  class: "compact-header",
                  onMouseover: ($event) => showPopover(item.description ?? "", $event),
                  onMouseleave: hidePopover
                }, [
                  createTextVNode(toDisplayString(item.title || item.key) + " ", 1),
                  item.required ? (openBlock(), createElementBlock("span", _hoisted_5$1, "*")) : createCommentVNode("", true)
                ], 40, _hoisted_4$1),
                createBaseVNode("div", _hoisted_6$1, [
                  createBaseVNode("div", _hoisted_7$1, [
                    withDirectives(createBaseVNode("input", {
                      "onUpdate:modelValue": ($event) => newArrayValue.value[item.key] = $event,
                      type: "text",
                      class: "minimal-input",
                      placeholder: `Add new ${item.title || item.key}`,
                      onKeyup: withKeys(($event) => addArrayValue(item), ["enter"])
                    }, null, 40, _hoisted_8$1), [
                      [vModelText, newArrayValue.value[item.key]]
                    ]),
                    createBaseVNode("button", {
                      class: "add-btn",
                      type: "button",
                      onClick: ($event) => addArrayValue(item)
                    }, "Add", 8, _hoisted_9$1)
                  ]),
                  createBaseVNode("div", _hoisted_10$1, [
                    (openBlock(true), createElementBlock(Fragment, null, renderList(getArrayValues(item), (value, valueIndex) => {
                      return openBlock(), createElementBlock("div", {
                        key: valueIndex,
                        class: "item-box"
                      }, [
                        createTextVNode(toDisplayString(value) + " ", 1),
                        createBaseVNode("span", {
                          class: "remove-btn",
                          onClick: ($event) => removeArrayValue(item, valueIndex)
                        }, "x", 8, _hoisted_11$1)
                      ]);
                    }), 128))
                  ])
                ])
              ])) : item.oneOf ? (openBlock(), createElementBlock("div", _hoisted_12$1, [
                createBaseVNode("div", {
                  class: "compact-header",
                  onMouseover: ($event) => showPopover(item.description ?? "", $event),
                  onMouseleave: hidePopover
                }, [
                  createTextVNode(toDisplayString(item.title || item.key) + " ", 1),
                  item.required ? (openBlock(), createElementBlock("span", _hoisted_14$1, "*")) : createCommentVNode("", true)
                ], 40, _hoisted_13$1),
                createVNode(DropDownGeneric, {
                  modelValue: selectedValues.value[index],
                  "onUpdate:modelValue": ($event) => selectedValues.value[index] = $event,
                  "option-list": item.oneOf.map((opt) => opt.title),
                  "allow-other": false,
                  style: { "width": "100%", "margin-bottom": "8px" },
                  onChange: (value) => updateSelectedOption(item, value, index)
                }, null, 8, ["modelValue", "onUpdate:modelValue", "option-list", "onChange"]),
                item.selectedOption !== void 0 ? (openBlock(), createElementBlock("div", _hoisted_15, [
                  (openBlock(true), createElementBlock(Fragment, null, renderList(item.oneOf[item.selectedOption].properties, (property, propKey) => {
                    return openBlock(), createElementBlock("div", {
                      key: propKey,
                      class: "nested-item"
                    }, [
                      propKey !== "auth_type" ? (openBlock(), createElementBlock(Fragment, { key: 0 }, [
                        createBaseVNode("div", {
                          class: "compact-header",
                          onMouseover: ($event) => showPopover(property.description, $event),
                          onMouseleave: hidePopover
                        }, [
                          createTextVNode(toDisplayString(property.title || propKey) + " ", 1),
                          isRequired(item.oneOf[item.selectedOption], propKey) ? (openBlock(), createElementBlock("span", _hoisted_17, "*")) : createCommentVNode("", true)
                        ], 40, _hoisted_16),
                        withDirectives(createBaseVNode("input", {
                          "onUpdate:modelValue": ($event) => item.input_value[propKey] = $event,
                          type: property.airbyte_secret ? "password" : "text",
                          class: "minimal-input",
                          placeholder: property.title || propKey
                        }, null, 8, _hoisted_18), [
                          [vModelDynamic, item.input_value[propKey]]
                        ])
                      ], 64)) : createCommentVNode("", true)
                    ]);
                  }), 128))
                ])) : createCommentVNode("", true)
              ])) : !item.properties || item.properties.length === 0 ? (openBlock(), createElementBlock("div", _hoisted_19, [
                createBaseVNode("div", {
                  class: "compact-header",
                  onMouseover: ($event) => showPopover(item.description ?? "", $event),
                  onMouseleave: hidePopover
                }, [
                  createTextVNode(toDisplayString(item.title || item.key) + " ", 1),
                  item.required ? (openBlock(), createElementBlock("span", _hoisted_21, "*")) : createCommentVNode("", true)
                ], 40, _hoisted_20),
                withDirectives(createBaseVNode("input", {
                  "onUpdate:modelValue": ($event) => item.input_value = $event,
                  type: item.airbyte_secret ? "password" : "text",
                  class: "minimal-input",
                  placeholder: item.title || item.key
                }, null, 8, _hoisted_22), [
                  [vModelDynamic, item.input_value]
                ])
              ])) : (openBlock(), createElementBlock("div", _hoisted_23, [
                createBaseVNode("button", {
                  class: normalizeClass(["minimal-header", { "is-open": item.isOpen }]),
                  onClick: ($event) => toggle(index)
                }, [
                  createBaseVNode("span", _hoisted_25, toDisplayString(item.isOpen ? "−" : "+"), 1),
                  createTextVNode(" " + toDisplayString(item.title) + " ", 1),
                  item.required ? (openBlock(), createElementBlock("span", _hoisted_26, "*")) : createCommentVNode("", true)
                ], 10, _hoisted_24),
                item.isOpen && item.properties && item.properties.length > 0 ? (openBlock(), createElementBlock("div", _hoisted_27, [
                  (openBlock(true), createElementBlock(Fragment, null, renderList(item.properties, (property, propIndex) => {
                    return openBlock(), createElementBlock("div", {
                      key: propIndex,
                      class: "nested-item"
                    }, [
                      createBaseVNode("div", {
                        class: "compact-header",
                        onMouseover: ($event) => showPopover(property.description, $event),
                        onMouseleave: hidePopover
                      }, [
                        createTextVNode(toDisplayString(property.key) + " ", 1),
                        property.required ? (openBlock(), createElementBlock("span", _hoisted_29, "*")) : createCommentVNode("", true)
                      ], 40, _hoisted_28),
                      withDirectives(createBaseVNode("input", {
                        "onUpdate:modelValue": ($event) => property.input_value = $event,
                        type: property.airbyte_secret ? "password" : "text",
                        class: "minimal-input",
                        placeholder: property.key
                      }, null, 8, _hoisted_30), [
                        [vModelDynamic, property.input_value]
                      ])
                    ]);
                  }), 128))
                ])) : createCommentVNode("", true)
              ]))
            ]);
          }), 128))
        ]),
        popover.value.show ? (openBlock(), createElementBlock("div", {
          key: 0,
          class: "minimal-popover",
          style: normalizeStyle({ top: popover.value.y + "px", left: popover.value.x + "px" })
        }, toDisplayString(popover.value.content), 5)) : createCommentVNode("", true)
      ]);
    };
  }
});
const airbyteConfigForm_vue_vue_type_style_index_0_scoped_b2f2d704_lang = "";
const AirbyteForm = /* @__PURE__ */ _export_sfc(_sfc_main$2, [["__scopeId", "data-v-b2f2d704"]]);
const _hoisted_1 = { key: 0 };
const _hoisted_2 = { class: "listbox-wrapper to-front" };
const _hoisted_3 = { key: 0 };
const _hoisted_4 = { class: "listbox-subtitle flex justify-between items-center" };
const _hoisted_5 = { class: "flex items-center gap-2" };
const _hoisted_6 = { class: "material-icons" };
const _hoisted_7 = { class: "flex gap-2" };
const _hoisted_8 = ["disabled"];
const _hoisted_9 = { class: "material-icons" };
const _hoisted_10 = {
  key: 1,
  class: "config-section"
};
const _hoisted_11 = {
  key: 1,
  class: "stream-section"
};
const _hoisted_12 = ["disabled"];
const _hoisted_13 = {
  key: 2,
  class: "stream-section"
};
const _hoisted_14 = {
  key: 1,
  class: "config-section"
};
const _sfc_main$1 = /* @__PURE__ */ defineComponent({
  __name: "airbyteReader",
  props: {
    nodeId: {}
  },
  setup(__props, { expose: __expose }) {
    const nodeStore = useNodeStore();
    const nodeExternalSource = ref(null);
    const backupAirbyteConfig = ref(null);
    const sourceSelected = ref(false);
    const availableConnectors = ref([]);
    const isConfigCollapsed = ref(false);
    const availableConfigs = ref([]);
    const loadedConnectors = ref(false);
    const connectorSelected = ref(false);
    const initialSelectedStream = ref(null);
    const inputValues = ref(null);
    const selectedConnector = ref("");
    const isFetchingStreams = ref(false);
    const isValidating = ref(false);
    const validationMessage = ref("");
    const validationStatus = ref("success");
    const airbyteConfigTemplate = ref(null);
    const airbyteConfig = ref(null);
    const getConnectors = async () => {
      availableConnectors.value = await getAirbyteConnectors();
      loadedConnectors.value = true;
    };
    const getAvailableConfigs = async () => {
      availableConfigs.value = await getAirbyteAvailableConfigs();
    };
    getAvailableConfigs();
    getConnectors();
    const validateConfig = async () => {
      var _a;
      if (!((_a = airbyteConfig.value) == null ? void 0 : _a.parsed_config))
        return;
      isValidating.value = true;
      validationMessage.value = "";
      try {
        await validateSelection();
        validationStatus.value = "success";
        validationMessage.value = "Configuration validated successfully";
      } catch (error) {
        validationStatus.value = "error";
        validationMessage.value = error instanceof Error ? error.message : "Validation failed";
      } finally {
        isValidating.value = false;
        setTimeout(() => {
          validationMessage.value = "";
        }, 5e3);
      }
    };
    const resetConfig = async () => {
      if (!confirm("Are you sure you want to reset all settings? This cannot be undone.") || !backupAirbyteConfig.value)
        return;
      if (!backupAirbyteConfig.value) {
        console.error("Backup config is missing");
        return;
      }
      airbyteConfig.value = { ...backupAirbyteConfig.value };
      selectedConnector.value = backupAirbyteConfig.value.source_name;
      initialSelectedStream.value = backupAirbyteConfig.value.selected_stream;
      const connectorInputData = await getAirbyteConnectorTemplate(selectedConnector.value);
      if (!connectorInputData)
        return;
      airbyteConfigTemplate.value = connectorInputData;
      sourceSelected.value = true;
    };
    const fetchAvailableStreams = async () => {
      var _a;
      if (!((_a = airbyteConfig.value) == null ? void 0 : _a.parsed_config))
        return;
      isFetchingStreams.value = true;
      try {
        inputValues.value = getConfigSettings(airbyteConfig.value.parsed_config);
        airbyteConfig.value.mapped_config_spec = inputValues.value;
        await setAirbyteConfigGetStreams(airbyteConfig.value);
        airbyteConfigTemplate.value = await getAirbyteConnectorTemplate(selectedConnector.value);
      } catch (error) {
        console.error("Error fetching streams:", error);
      } finally {
        isFetchingStreams.value = false;
      }
    };
    const loadNodeData = async (nodeId) => {
      var _a;
      const nodeResult = await nodeStore.getNodeData(nodeId, false);
      nodeExternalSource.value = nodeResult == null ? void 0 : nodeResult.setting_input;
      if (!((_a = nodeExternalSource.value) == null ? void 0 : _a.is_setup) || !nodeExternalSource.value.source_settings)
        return;
      airbyteConfig.value = nodeExternalSource.value.source_settings;
      backupAirbyteConfig.value = { ...airbyteConfig.value };
      selectedConnector.value = airbyteConfig.value.source_name;
      sourceSelected.value = true;
      initialSelectedStream.value = airbyteConfig.value.selected_stream;
      const connectorInputData = await getAirbyteConnectorTemplate(selectedConnector.value);
      if (!connectorInputData)
        return;
      airbyteConfigTemplate.value = connectorInputData;
      if (!airbyteConfig.value.parsed_config) {
        airbyteConfig.value.parsed_config = computeSchema(airbyteConfigTemplate.value.config_spec);
      }
      if (!connectorInputData.available_streams && airbyteConfig.value.parsed_config) {
        await fetchAvailableStreams();
      }
    };
    const selectConnector = () => {
      var _a;
      if (((_a = airbyteConfig.value) == null ? void 0 : _a.source_name) === selectedConnector.value)
        return;
      if (availableConfigs.value.includes("source-" + selectedConnector.value)) {
        getConfig();
        return;
      }
      sourceSelected.value = false;
      connectorSelected.value = true;
      airbyteConfigTemplate.value = null;
      airbyteConfig.value = null;
    };
    const getConfig = async () => {
      connectorSelected.value = false;
      sourceSelected.value = true;
      const connectorInputData = await getAirbyteConnectorTemplate(selectedConnector.value);
      if (!connectorInputData)
        return;
      airbyteConfigTemplate.value = connectorInputData;
      const parsed_config = computeSchema(airbyteConfigTemplate.value.config_spec);
      airbyteConfig.value = {
        parsed_config,
        mapped_config_spec: {},
        config_mode: "in_line",
        selected_stream: "",
        source_name: selectedConnector.value
      };
    };
    const validateSelection = async () => {
      if (!nodeExternalSource.value || !airbyteConfig.value)
        throw new Error("Invalid configuration");
      nodeExternalSource.value.is_setup = true;
      nodeExternalSource.value.source_settings = airbyteConfig.value;
      nodeExternalSource.value.source_settings.mapped_config_spec = getConfigSettings(
        airbyteConfig.value.parsed_config
      );
      if (initialSelectedStream.value != airbyteConfig.value.selected_stream) {
        nodeExternalSource.value.source_settings.fields = [];
      }
      await nodeStore.updateSettings(nodeExternalSource);
    };
    const pushNodeData = async () => {
      if (!nodeExternalSource.value || !airbyteConfig.value)
        return;
      nodeExternalSource.value.is_setup = true;
      nodeExternalSource.value.source_settings = airbyteConfig.value;
      nodeExternalSource.value.source_settings.mapped_config_spec = getConfigSettings(
        airbyteConfig.value.parsed_config
      );
      if (initialSelectedStream.value != airbyteConfig.value.selected_stream) {
        nodeExternalSource.value.source_settings.fields = [];
      }
      await nodeStore.updateSettings(nodeExternalSource);
    };
    __expose({
      loadNodeData,
      pushNodeData
    });
    return (_ctx, _cache) => {
      const _component_el_option = resolveComponent("el-option");
      const _component_el_select = resolveComponent("el-select");
      return nodeExternalSource.value ? (openBlock(), createElementBlock("div", _hoisted_1, [
        createVNode(GenericNodeSettings, {
          modelValue: nodeExternalSource.value,
          "onUpdate:modelValue": _cache[3] || (_cache[3] = ($event) => nodeExternalSource.value = $event)
        }, {
          default: withCtx(() => {
            var _a, _b, _c, _d;
            return [
              _cache[8] || (_cache[8] = createBaseVNode("div", { class: "listbox-wrapper" }, [
                createBaseVNode("div", { class: "listbox-subtitle" }, [
                  createBaseVNode("img", {
                    src: _imports_0,
                    alt: "Airbyte Icon",
                    class: "file-icon"
                  }),
                  createBaseVNode("span", null, "Get data from Airbyte supported source")
                ]),
                createBaseVNode("div", { class: "attention-notice" }, [
                  createBaseVNode("span", { class: "warning-icon" }, "⚠️"),
                  createBaseVNode("span", { class: "docker-notice" }, "Running Docker instance required")
                ])
              ], -1)),
              createBaseVNode("div", _hoisted_2, [
                createVNode(DropDownGeneric, {
                  modelValue: selectedConnector.value,
                  "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => selectedConnector.value = $event),
                  "option-list": availableConnectors.value,
                  title: "Load data from",
                  "is-loading": !loadedConnectors.value,
                  "allow-other": false,
                  onChange: selectConnector
                }, null, 8, ["modelValue", "option-list", "is-loading"])
              ]),
              sourceSelected.value ? (openBlock(), createElementBlock("div", _hoisted_3, [
                createBaseVNode("div", _hoisted_4, [
                  createBaseVNode("div", _hoisted_5, [
                    _cache[4] || (_cache[4] = createBaseVNode("span", null, "Config settings", -1)),
                    createBaseVNode("button", {
                      class: "icon-button",
                      onClick: _cache[1] || (_cache[1] = ($event) => isConfigCollapsed.value = !isConfigCollapsed.value)
                    }, [
                      createBaseVNode("span", _hoisted_6, toDisplayString(isConfigCollapsed.value ? "expand_more" : "expand_less"), 1)
                    ])
                  ]),
                  createBaseVNode("div", _hoisted_7, [
                    ((_a = airbyteConfig.value) == null ? void 0 : _a.parsed_config) ? (openBlock(), createElementBlock("button", {
                      key: 0,
                      class: "secondary-button",
                      onClick: resetConfig
                    }, _cache[5] || (_cache[5] = [
                      createTextVNode(" Reset settings "),
                      createBaseVNode("span", { class: "material-icons" }, "restart_alt", -1)
                    ]))) : createCommentVNode("", true),
                    ((_b = airbyteConfig.value) == null ? void 0 : _b.parsed_config) ? (openBlock(), createElementBlock("button", {
                      key: 1,
                      class: "secondary-button",
                      disabled: isValidating.value,
                      onClick: validateConfig
                    }, [
                      createTextVNode(toDisplayString(isValidating.value ? "Validating..." : "Validate") + " ", 1),
                      createBaseVNode("span", {
                        class: normalizeClass(["material-icons", { spin: isValidating.value }])
                      }, "check_circle", 2)
                    ], 8, _hoisted_8)) : createCommentVNode("", true)
                  ])
                ]),
                validationMessage.value ? (openBlock(), createElementBlock("div", {
                  key: 0,
                  class: normalizeClass(["validation-banner", validationStatus.value])
                }, [
                  createBaseVNode("span", _hoisted_9, toDisplayString(validationStatus.value === "success" ? "check_circle" : "warning"), 1),
                  createTextVNode(" " + toDisplayString(validationMessage.value), 1)
                ], 2)) : createCommentVNode("", true),
                ((_c = airbyteConfig.value) == null ? void 0 : _c.parsed_config) ? (openBlock(), createElementBlock("div", _hoisted_10, [
                  !isConfigCollapsed.value ? (openBlock(), createBlock(AirbyteForm, {
                    key: 0,
                    ref: "airbyteForm",
                    "parsed-config": airbyteConfig.value.parsed_config
                  }, null, 8, ["parsed-config"])) : createCommentVNode("", true),
                  !((_d = airbyteConfigTemplate.value) == null ? void 0 : _d.available_streams) ? (openBlock(), createElementBlock("div", _hoisted_11, [
                    createBaseVNode("button", {
                      class: "primary-button",
                      disabled: isFetchingStreams.value,
                      onClick: fetchAvailableStreams
                    }, [
                      createTextVNode(toDisplayString(isFetchingStreams.value ? "Loading streams..." : "Load available streams") + " ", 1),
                      createBaseVNode("span", {
                        class: normalizeClass(["material-icons", { spin: isFetchingStreams.value }])
                      }, "refresh", 2)
                    ], 8, _hoisted_12)
                  ])) : (openBlock(), createElementBlock("div", _hoisted_13, [
                    _cache[6] || (_cache[6] = createBaseVNode("div", { class: "listbox-subtitle" }, [
                      createBaseVNode("span", null, "Select stream")
                    ], -1)),
                    createVNode(_component_el_select, {
                      modelValue: airbyteConfig.value.selected_stream,
                      "onUpdate:modelValue": _cache[2] || (_cache[2] = ($event) => airbyteConfig.value.selected_stream = $event),
                      placeholder: "Select a stream",
                      size: "small",
                      class: "stream-select"
                    }, {
                      default: withCtx(() => [
                        (openBlock(true), createElementBlock(Fragment, null, renderList(airbyteConfigTemplate.value.available_streams, (stream) => {
                          return openBlock(), createBlock(_component_el_option, {
                            key: stream,
                            label: stream,
                            value: stream
                          }, null, 8, ["label", "value"]);
                        }), 128))
                      ]),
                      _: 1
                    }, 8, ["modelValue"])
                  ]))
                ])) : (openBlock(), createBlock(unref(CodeLoader), { key: 2 }))
              ])) : connectorSelected.value ? (openBlock(), createElementBlock("div", _hoisted_14, [
                createBaseVNode("button", {
                  class: "file-upload-label",
                  onClick: getConfig
                }, _cache[7] || (_cache[7] = [
                  createTextVNode(" Load settings "),
                  createBaseVNode("span", { class: "material-icons file-icon" }, "refresh", -1)
                ]))
              ])) : createCommentVNode("", true)
            ];
          }),
          _: 1,
          __: [8]
        }, 8, ["modelValue"])
      ])) : createCommentVNode("", true);
    };
  }
});
const airbyteReader_vue_vue_type_style_index_0_scoped_9dcbd94f_lang = "";
const airbyteSource = /* @__PURE__ */ _export_sfc(_sfc_main$1, [["__scopeId", "data-v-9dcbd94f"]]);
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "AirbyteReader",
  props: {
    nodeId: {
      type: Number,
      required: true
    }
  },
  setup(__props) {
    const nodeStore = useNodeStore();
    const props = __props;
    const childComp = ref(null);
    const el = ref(null);
    const drawer = ref(false);
    const closeOnDrawer = () => {
      var _a;
      (_a = childComp.value) == null ? void 0 : _a.pushNodeData();
      drawer.value = false;
      nodeStore.isDrawerOpen = false;
    };
    const openDrawer = async () => {
      if (nodeStore.node_id === props.nodeId) {
        return;
      }
      console.log("openDrawer");
      drawer.value = true;
      const drawerOpen = nodeStore.isDrawerOpen;
      nodeStore.isDrawerOpen = true;
      await nextTick();
      if (nodeStore.node_id === props.nodeId && drawerOpen) {
        console.log("No need to load data");
        return;
      }
      if (childComp.value) {
        await childComp.value.loadNodeData(props.nodeId);
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
          ref: "nodeButton",
          "node-id": __props.nodeId,
          "image-src": "airbyte.png",
          title: `${__props.nodeId}: External source`,
          onClick: openDrawer
        }, null, 8, ["node-id", "title"]),
        drawer.value ? (openBlock(), createBlock(Teleport, {
          key: 0,
          to: "#nodesettings"
        }, [
          createVNode(NodeTitle, {
            title: "External source",
            intro: "Import data from an external source"
          }),
          createVNode(airbyteSource, {
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
