import { C as ColumnSelector } from "./dropDown-d5a4014c.js";
import { d as defineComponent, r as ref, m as watch, c as openBlock, e as createElementBlock, t as toDisplayString, i as createCommentVNode, p as createBaseVNode, f as createVNode, _ as _export_sfc } from "./index-f25c9283.js";
const _hoisted_1 = {
  key: 0,
  class: "label"
};
const _hoisted_2 = { class: "select-wrapper" };
const _sfc_main = /* @__PURE__ */ defineComponent({
  __name: "dropDownGeneric",
  props: {
    modelValue: {
      type: String,
      default: "NewField"
    },
    optionList: {
      type: Array,
      required: true
    },
    title: {
      type: String,
      default: ""
    },
    allowOther: {
      type: Boolean,
      default: true
    },
    placeholder: {
      type: String,
      default: "Select an option"
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ["update:modelValue", "change"],
  setup(__props, { emit: __emit }) {
    const props = __props;
    const emit = __emit;
    const localSelectedValue = ref(props.modelValue);
    watch(
      () => props.modelValue,
      (newVal) => {
        localSelectedValue.value = newVal;
      }
    );
    watch(localSelectedValue, (newVal) => {
      emit("update:modelValue", newVal);
      emit("change", newVal);
    });
    return (_ctx, _cache) => {
      return openBlock(), createElementBlock("div", null, [
        __props.title !== "" ? (openBlock(), createElementBlock("p", _hoisted_1, toDisplayString(__props.title), 1)) : createCommentVNode("", true),
        createBaseVNode("div", _hoisted_2, [
          createVNode(ColumnSelector, {
            modelValue: localSelectedValue.value,
            "onUpdate:modelValue": _cache[0] || (_cache[0] = ($event) => localSelectedValue.value = $event),
            "column-options": __props.optionList,
            "allow-other": __props.allowOther,
            placeholder: __props.placeholder,
            "is-loading": __props.isLoading
          }, null, 8, ["modelValue", "column-options", "allow-other", "placeholder", "is-loading"])
        ])
      ]);
    };
  }
});
const dropDownGeneric_vue_vue_type_style_index_0_scoped_f2958f57_lang = "";
const DropDownGeneric = /* @__PURE__ */ _export_sfc(_sfc_main, [["__scopeId", "data-v-f2958f57"]]);
export {
  DropDownGeneric as D
};
