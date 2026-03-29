<template>
  <div class="page">
    <div class="card">
      <h1 class="title">Регистрация</h1>

      <form class="form" @submit.prevent="registerUser">
        <div class="row row--stack">
          <div class="row__line">
            <label>Email</label>
            <input
              v-model.trim="email"
              type="text"
              class="input"
              placeholder="example@mail.com"
              @blur="validateEmail"
              @input="validateEmail"
            />
          </div>

          <p v-if="emailError" class="error-text">
            Введите корректный email
          </p>
        </div>

        <div class="row">
          <label>Логин</label>
          <input
            v-model.trim="login"
            class="input"
            placeholder="Введите логин"
            autocomplete="username"
            required
          />
        </div>

        <div class="row">
          <label>Пароль</label>

          <div class="password-wrapper">
            <div class="input-wrap">
              <input
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="input"
                :class="{ error: passwordInvalid && password.length > 0 }"
                placeholder="Минимум 8 символов, A-Z и цифра"
                autocomplete="new-password"
                required
                @focus="showRules = true"
                @blur="onPasswordBlur"
                @input="checkPassword"
              />

              <button
                class="toggle"
                type="button"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Скрыть пароль' : 'Показать пароль'"
              >
                {{ showPassword ? "Скрыть" : "Показать" }}
              </button>
            </div>

            <div v-if="showRules" class="password-tooltip" role="status" aria-live="polite">
              <p :class="{ ok: rules.length }">Минимум 8 символов</p>
              <p :class="{ ok: rules.upper }">Хотя бы одна заглавная буква (A–Z)</p>
              <p :class="{ ok: rules.number }">Хотя бы одна цифра (0–9)</p>
              <p class="danger" :class="{ ok: !rules.cyrillic }">
                Только латинские буквы (русские символы не допускаются)
              </p>
            </div>
          </div>
        </div>

        <div class="row row--stack">
          <div class="row__line">
            <label>Подтверждение</label>
            <input
              v-model="password2"
              :type="showPassword ? 'text' : 'password'"
              class="input"
              :class="{ error: passwordError && password2.length > 0 }"
              placeholder="Повторите пароль"
              autocomplete="new-password"
              required
              @input="validatePasswords"
            />
          </div>

          <p v-if="passwordError" class="error-text">
            Пароли не совпадают
          </p>
        </div>

        <button class="btn" type="submit" :disabled="submitDisabled || isSubmitting">
          {{ isSubmitting ? "Отправляем..." : "Зарегистрироваться" }}
        </button>

        <p v-if="submitError" class="submit-error">
          {{ submitError }}
        </p>

        <p v-if="submitSuccess" class="submit-success">
          {{ submitSuccess }}
        </p>

        <p class="login">
          Уже есть аккаунт?
          <router-link to="/login">Войти</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from "vue";
import { useRouter } from "vue-router";
import store from "../store";
import {
  registerUser as registerUserRequest,
  saveUser,
  setTokens,
} from "../utils/auth";

const router = useRouter();

const email = ref("");
const login = ref("");
const password = ref("");
const password2 = ref("");
const showPassword = ref(false);
const showRules = ref(false);
const passwordError = ref(false);
const rules = reactive({
  length: false,
  upper: false,
  number: false,
  cyrillic: false,
});
const emailError = ref(false);
const submitError = ref("");
const submitSuccess = ref("");
const isSubmitting = ref(false);
const passwordInvalid = ref(false);

function validateEmail(){
  if(email.value === ""){
    emailError.value = false
    return
  }

  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  emailError.value = !pattern.test(email.value)
}

function checkPassword() {
  const value = password.value;

  rules.length = value.length >= 8;
  rules.upper = /[A-Z]/.test(value);
  rules.number = /\d/.test(value);
  rules.cyrillic = /[а-яА-ЯЁё]/.test(value);

  passwordInvalid.value =
    !rules.length || !rules.upper || !rules.number || rules.cyrillic;

  validatePasswords();
}

function validatePasswords() {
  if (password2.value.length === 0) {
    passwordError.value = false;
    return;
  }
  passwordError.value = password.value !== password2.value;
}

function onPasswordBlur(e) {
  setTimeout(() => {
    const wrapper = e?.target?.closest?.(".password-wrapper");
    if (wrapper && wrapper.contains(document.activeElement)) return;
    showRules.value = false;
  }, 0);
}

const submitDisabled = computed(() => {
  if (password.value.length === 0 || password2.value.length === 0) return false;
  return passwordInvalid.value || passwordError.value;
});

async function registerUser() {
  submitError.value = "";
  submitSuccess.value = "";

  validateEmail();
  checkPassword();
  validatePasswords();

  if (emailError.value || passwordInvalid.value || passwordError.value) return;

  const payload = {
    email: email.value,
    username: login.value,
    password: password.value,
  };

  try {
    isSubmitting.value = true;
    const response = await registerUserRequest(payload);

    if (response?.access && response?.refresh) {
      setTokens({
        access: response.access,
        refresh: response.refresh,
      });
    }

    if (response?.user) {
      saveUser(response.user);
      store.commit("SET_USER", response.user);
    }

    store.commit("SET_AUTHENTICATED", true);
    submitSuccess.value = "Регистрация прошла успешно.";

    setTimeout(() => {
      router.push("/lk");
    }, 700);
  } catch (error) {
    submitError.value = error.message || "Не удалось зарегистрироваться";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.page{
  min-height: calc(100vh - 70px);
  display: grid;
  place-items: center;
  background: #f6f7fb;
  padding: 30px 16px;
}

.card{
  width: 560px;
  max-width: 100%;
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.title{
  font-size: 22px;
  font-weight: 700;
  margin: 0 0 18px;
}

.form{
  display: flex;
  flex-direction: column;
}

.row{
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.row label{
  width: 180px;
  font-size: 14px;
  color: #111827;
}

.input{
  flex: 1;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  outline: none;
  background: #fff;
}

.input:focus{
  border-color: rgba(59,130,246,.55);
  box-shadow: 0 0 0 4px rgba(59,130,246,.14);
}

.extra{
  margin-top: 6px;
}

.btn{
  margin-top: 14px;
  padding: 10px;
  background: #3b5bdb;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
}
.btn:disabled{
  opacity: .6;
  cursor: not-allowed;
}

.login{
  margin-top: 10px;
  font-size: 13px;
  color: #374151;
}

.login a{
  color: #4f46e5;
  text-decoration: none;
}
.login a:hover{
  text-decoration: underline;
}

.error{
  border: 1px solid #ef4444 !important;
  box-shadow: 0 0 0 4px rgba(239,68,68,.12) !important;
}

.row--stack{
  display: block;
  margin-bottom: 8px;
}
.row__line{
  display: flex;
  align-items: center;
  gap: 12px;
}
.error-text{
  margin: 6px 0 0 192px;
  font-size: 12px;
  color: #ef4444;
}

.password-wrapper{
  position: relative;
  flex: 1;
}

.input-wrap{
  position: relative;
  display: flex;
  align-items: center;
}
.input-wrap .input{
  width: 100%;
  padding-right: 92px;
}

.toggle{
  position: absolute;
  right: 8px;
  height: 30px;
  padding: 0 10px;
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,.12);
  background: #f3f4f6;
  font-size: 12px;
  cursor: pointer;
}
.toggle:hover{ background: #e9ecef; }

.password-tooltip{
  position: absolute;
  top: 46px;
  left: 0;
  width: 320px;
  background: #fff;
  border: 1px solid rgba(0,0,0,.12);
  border-radius: 10px;
  padding: 10px 12px;
  box-shadow: 0 10px 24px rgba(0,0,0,.14);
  z-index: 1000;
  font-size: 12px;
}

.password-tooltip p{
  margin: 3px 0;
  color: #9ca3af;
}

.password-tooltip p.ok{
  color: #16a34a;
}

.password-tooltip p.danger{
  color: #ef4444;
}
.password-tooltip p.danger.ok{
  color: #16a34a;
}

.submit-error{
  margin: 10px 0 0;
  color: #dc2626;
  font-size: 13px;
}

.submit-success{
  margin: 10px 0 0;
  color: #15803d;
  font-size: 13px;
}
</style>
