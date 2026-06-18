<script setup lang="ts">
import { computed, onMounted, reactive } from 'vue';
import { loginModuleRecord } from '@/constants/app';
import { useAuthStore } from '@/store/modules/auth';
import { useRouterPush } from '@/hooks/common/router';
import { useFormRules, useAntdvForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'PwdLogin'
});

const authStore = useAuthStore();
const { toggleLoginModule } = useRouterPush();
const { formRef, validate } = useAntdvForm();

interface FormModel {
  userName: string;
  password: string;
  captcha: string;
}

const model: FormModel = reactive({
  userName: 'admin',
  password: '123456',
  captcha: ''
});

const rules = computed<Record<keyof FormModel, App.Global.FormRule[]>>(() => {
  // inside computed to make locale reactive, if not apply i18n, you can define it without computed
  const { formRules, createRequiredRule } = useFormRules();

  return {
    userName: formRules.userName,
    password: formRules.pwd,
    captcha: authStore.captcha.is_enabled ? [createRequiredRule($t('form.code.required'))] : []
  };
});

async function handleSubmit() {
  await validate();
  await authStore.login(model.userName, model.password, model.captcha, authStore.captcha.uuid);
}

type AccountKey = 'admin' | 'user';

interface Account {
  key: AccountKey;
  label: string;
  userName: string;
  password: string;
}

const accounts = computed<Account[]>(() => [
  {
    key: 'admin',
    label: $t('page.login.pwdLogin.admin'),
    userName: 'admin',
    password: '123456'
  },
  {
    key: 'user',
    label: $t('page.login.pwdLogin.user'),
    userName: 'test',
    password: '123456'
  }
]);

function handleAccountLogin(account: Account) {
  model.userName = account.userName;
  model.password = account.password;
}

onMounted(() => {
  authStore.loadCaptcha();
});
</script>

<template>
  <AForm ref="formRef" :model="model" :rules="rules" @keyup.enter="handleSubmit">
    <AFormItem name="userName">
      <AInput v-model:value="model.userName" size="large" :placeholder="$t('page.login.common.userNamePlaceholder')" />
    </AFormItem>
    <AFormItem name="password">
      <AInputPassword
        v-model:value="model.password"
        size="large"
        :placeholder="$t('page.login.common.passwordPlaceholder')"
      />
    </AFormItem>
    <AFormItem v-if="authStore.captcha.is_enabled" name="captcha">
      <div class="flex-y-center gap-12px">
        <AInput v-model:value="model.captcha" size="large" :placeholder="$t('page.login.common.codePlaceholder')" />
        <AButton
          html-type="button"
          class="h-40px min-w-120px overflow-hidden !p-0"
          :loading="authStore.captchaLoading"
          @click="authStore.loadCaptcha"
        >
          <img
            v-if="authStore.captcha.image"
            :src="authStore.captcha.image"
            alt="captcha"
            class="h-full w-full object-cover"
          />
          <span v-else>{{ $t('common.refresh') }}</span>
        </AButton>
      </div>
    </AFormItem>
    <ASpace vertical :size="24" class="w-full sa-login-action-space">
      <div class="flex-y-center justify-between">
        <ACheckbox>{{ $t('page.login.pwdLogin.rememberMe') }}</ACheckbox>
        <AButton type="text" @click="toggleLoginModule('reset-pwd')">
          {{ $t('page.login.pwdLogin.forgetPassword') }}
        </AButton>
      </div>
      <AButton type="primary" size="large" shape="round" block :loading="authStore.loginLoading" @click="handleSubmit">
        {{ $t('common.confirm') }}
      </AButton>
      <div class="flex-y-center justify-between gap-12px">
        <AButton class="flex-1" block @click="toggleLoginModule('code-login')">
          {{ $t(loginModuleRecord['code-login']) }}
        </AButton>
        <AButton class="flex-1" block @click="toggleLoginModule('register')">
          {{ $t(loginModuleRecord.register) }}
        </AButton>
      </div>
      <ADivider class="text-14px text-#666 !m-0">{{ $t('page.login.pwdLogin.otherAccountLogin') }}</ADivider>
      <div class="flex-center gap-12px">
        <AButton v-for="item in accounts" :key="item.key" type="primary" @click="handleAccountLogin(item)">
          {{ item.label }}
        </AButton>
      </div>
    </ASpace>
  </AForm>
</template>

<style scoped></style>
