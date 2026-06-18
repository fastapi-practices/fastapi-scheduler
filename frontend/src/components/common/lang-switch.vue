<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

defineOptions({
  name: 'LangSwitch'
});

interface Props {
  /** Current language */
  lang: App.I18n.LangType;
  /** Language options */
  langOptions: App.I18n.LangOption[];
  /** Show tooltip */
  showTooltip?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showTooltip: true
});

type Emits = {
  (e: 'changeLang', lang: App.I18n.LangType): void;
};

const emit = defineEmits<Emits>();

const tooltipContent = computed(() => {
  if (!props.showTooltip) return '';

  return $t('icon.lang');
});

/** Add bottom margin to all options except the last one for proper visual separation */
const dropdownOptions = computed(() => {
  const lastIndex = props.langOptions.length - 1;

  return props.langOptions.map((option, index) => ({
    ...option,
    props: {
      class: index < lastIndex ? 'mb-1' : undefined
    }
  }));
});

const dropdownMenu = computed(() => ({
  items: dropdownOptions.value,
  selectedKeys: [props.lang],
  onClick: handleMenuClick
}));

function changeLang(lang: App.I18n.LangType) {
  emit('changeLang', lang);
}

function handleMenuClick({ key }: { key: string | number }) {
  changeLang(key as App.I18n.LangType);
}
</script>

<template>
  <ADropdown :menu="dropdownMenu" :trigger="['hover']">
    <div>
      <ButtonIcon :tooltip-content="tooltipContent" tooltip-placement="left">
        <SvgIcon icon="heroicons:language" />
      </ButtonIcon>
    </div>
  </ADropdown>
</template>

<style scoped></style>
