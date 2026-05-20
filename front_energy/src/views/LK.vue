<template>
  <div class="lk">
    <div class="container">
      <div class="header">
        <div>
          <h1 class="title">Личный кабинет</h1>
          <p class="subtitle">Профиль пользователя и параметры аккаунта.</p>
        </div>

        <div class="actions">
          <button class="btn btn--ghost" @click="go('/')">На главную</button>
          <button class="btn btn--danger" @click="onLogout">Выйти</button>
        </div>
      </div>

      <section class="card">
        <div class="card__top">
          <h2 class="card__title">Профиль</h2>
          <button class="btn btn--ghost" @click="toggleEdit" :disabled="profileLoading || saveLoading">
            {{ isEditing ? "Скрыть форму" : "Изменить данные" }}
          </button>
        </div>

        <p v-if="profileLoading" class="hint">Загружаем профиль...</p>
        <p v-if="profileError" class="error-text">{{ profileError }}</p>
        <p v-if="saveSuccess" class="success-text">{{ saveSuccess }}</p>

        <div class="grid2">
          <div class="field">
            <span class="label">Логин</span>
            <div class="value-box">{{ profile.username || "Не заполнено" }}</div>
          </div>

          <div class="field">
            <span class="label">Email</span>
            <div class="value-box">{{ profile.email || "Не заполнено" }}</div>
          </div>

          <div class="field">
            <span class="label">Дата регистрации</span>
            <div class="value-box">{{ profile.dateJoined || "Не заполнено" }}</div>
          </div>

          <div class="field">
            <span class="label">Регион</span>
            <div class="value-box">{{ formatDisplay(serverProfile.region) }}</div>
          </div>

          <div class="field">
            <span class="label">Кто вы</span>
            <div class="value-box">{{ roleLabel(serverProfile.role) }}</div>
          </div>

          <div class="field">
            <span class="label">Название организации / института</span>
            <div class="value-box">{{ formatDisplay(serverProfile.organization) }}</div>
          </div>

          <div v-if="serverProfile.role === 'student'" class="field">
            <span class="label">Курс</span>
            <div class="value-box">{{ formatDisplay(serverProfile.course) }}</div>
          </div>

          <div v-if="serverProfile.role === 'student'" class="field">
            <span class="label">Направление</span>
            <div class="value-box">{{ formatDisplay(serverProfile.specialization) }}</div>
          </div>
        </div>
      </section>

      <section v-if="isEditing" class="card">
        <div class="card__top">
          <h2 class="card__title">Редактирование профиля</h2>
          <button class="btn" @click="saveProfile" :disabled="profileLoading || saveLoading">
            {{ saveLoading ? "Сохраняем..." : "Сохранить" }}
          </button>
        </div>

        <p class="hint">
          Здесь можно изменить данные расширенного профиля.
        </p>

        <div class="grid2">
          <label class="field">
            <span class="label">Регион</span>
            <select v-model="profile.region" class="input">
              <option value="">Выберите регион</option>
              <option v-for="region in regionOptions" :key="region.value" :value="region.value">
                {{ region.value }}
              </option>
            </select>
          </label>

          <label class="field">
            <span class="label">Кто вы</span>
            <select v-model="profile.role" class="input">
              <option value="">Выберите</option>
              <option value="student">Студент</option>
              <option value="teacher">Преподаватель</option>
              <option value="admin">Администратор</option>
            </select>
          </label>

          <label class="field">
            <span class="label">Название организации / института</span>
            <input v-model.trim="profile.organization" class="input" placeholder="Например: ИРНИТУ" />
          </label>

          <label v-if="profile.role === 'student'" class="field">
            <span class="label">Курс</span>
            <select v-model="profile.course" class="input">
              <option value="">Выберите курс</option>
              <option v-for="n in 6" :key="n" :value="String(n)">{{ n }}</option>
            </select>
          </label>

          <label v-if="profile.role === 'student'" class="field">
            <span class="label">Направление</span>
            <input v-model.trim="profile.specialization" class="input" placeholder="Например: Электроэнергетика" />
          </label>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import {
  fetchExtendedProfile,
  fetchProfile,
  getSavedUser,
  logout,
  updateExtendedProfile,
} from "../utils/auth";
import store from "../store";

const router = useRouter();

const profileError = ref("");
const profileLoading = ref(false);
const saveLoading = ref(false);
const saveSuccess = ref("");
const isEditing = ref(false);

const profile = reactive({
  username: "",
  email: "",
  dateJoined: "",
  region: "",
  role: "",
  organization: "",
  course: "",
  specialization: "",
});

const serverProfile = reactive({
  region: "",
  role: "",
  organization: "",
  course: "",
  specialization: "",
});

const regionOptions = computed(() => store.getters.staticRegions || []);
const roleLabels = {
  student: "Студент",
  teacher: "Преподаватель",
  admin: "Администратор",
};

function formatDisplay(value) {
  return value === "" || value === null || value === undefined ? "Не заполнено" : String(value);
}

function roleLabel(value) {
  return roleLabels[value] || "Не заполнено";
}

function applyAuthProfile(user) {
  if (!user || typeof user !== "object") {
    return;
  }

  profile.username = user.username || profile.username;
  profile.email = user.email || profile.email;
  profile.dateJoined = user.date_joined
    ? new Date(user.date_joined).toLocaleString("ru-RU")
    : profile.dateJoined;
}

function normalizeExtendedProfile(data) {
  if (!data) {
    return null;
  }

  if (data.data) {
    return normalizeExtendedProfile(data.data);
  }

  if (Array.isArray(data)) {
    return normalizeExtendedProfile(data[0] || null);
  }

  if (Array.isArray(data.results)) {
    return normalizeExtendedProfile(data.results[0] || null);
  }

  if (data.profile && typeof data.profile === "object") {
    return {
      username: data.username || "",
      email: data.email || "",
      region: data.profile.region || "",
      role: data.profile.role || "",
      organization: data.profile.organization || "",
      course: data.profile.course ?? "",
      specialization: data.profile.specialization || "",
    };
  }

  return data;
}

function applyExtendedProfile(user) {
  const normalized = normalizeExtendedProfile(user);

  if (!normalized || typeof normalized !== "object") {
    return;
  }

  if (normalized.username) {
    profile.username = normalized.username;
  }

  if (normalized.email) {
    profile.email = normalized.email;
  }

  serverProfile.region = normalized.region || "";
  serverProfile.role = normalized.role || "";
  serverProfile.organization = normalized.organization || "";
  serverProfile.course = normalized.course !== "" && normalized.course !== null && normalized.course !== undefined
    ? String(normalized.course)
    : "";
  serverProfile.specialization = normalized.specialization || "";

  profile.region = normalized.region || "";
  profile.role = normalized.role || "";
  profile.organization = normalized.organization || "";
  profile.course = normalized.course !== "" && normalized.course !== null && normalized.course !== undefined
    ? String(normalized.course)
    : "";
  profile.specialization = normalized.specialization || "";
}

function go(path) {
  router.push(path);
}

function toggleEdit() {
  isEditing.value = !isEditing.value;
}

async function onLogout() {
  await logout();
  store.commit("SET_AUTHENTICATED", false);
  store.commit("SET_USER", null);
  router.push("/login");
}

async function loadProfile() {
  profileError.value = "";
  profileLoading.value = true;

  try {
    const [authUser, extendedProfile] = await Promise.all([
      fetchProfile(),
      fetchExtendedProfile(),
    ]);

    store.commit("SET_USER", authUser);
    applyAuthProfile(authUser);
    applyExtendedProfile(extendedProfile);
  } catch (error) {
    profileError.value = error.message || "Не удалось загрузить профиль";
  } finally {
    profileLoading.value = false;
  }
}

async function saveProfile() {
  profileError.value = "";
  saveSuccess.value = "";
  saveLoading.value = true;

  try {
    const payload = {
      region: profile.region || "",
      role: profile.role || "",
      organization: profile.organization || "",
    };

    if (profile.role === "student") {
      if (profile.course) {
        payload.course = Number(profile.course);
      }

      payload.specialization = profile.specialization || "";
    }

    const updated = await updateExtendedProfile(payload);
    applyExtendedProfile(updated);

    const refreshed = await fetchExtendedProfile();
    applyExtendedProfile(refreshed);
    saveSuccess.value = "Профиль сохранён";
    isEditing.value = false;
  } catch (error) {
    profileError.value = error.message || "Не удалось сохранить профиль";
  } finally {
    saveLoading.value = false;
  }
}

onMounted(() => {
  const savedUser = store.state.user || getSavedUser();
  applyAuthProfile(savedUser);
  loadProfile();
});
</script>

<style scoped>
.lk{
  min-height: calc(100vh - 70px);
  background: #f6f7fb;
  padding: 22px 16px 40px;
}

.container{
  max-width: 1100px;
  margin: 0 auto;
  display: grid;
  gap: 12px;
}

.header{
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap: 16px;
  padding: 6px 2px 10px;
}

.title{
  margin: 0;
  font-size: 28px;
  font-weight: 900;
  color: #111827;
}

.subtitle{
  margin: 6px 0 0;
  color:#6b7280;
  font-size: 13px;
}

.actions{
  display:flex;
  gap: 10px;
  flex-wrap: wrap;
}

.card{
  background:#fff;
  border:1px solid rgba(17,24,39,.08);
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(17,24,39,.07);
  padding: 16px;
}

.card__top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;
}

.card__title{
  margin: 0;
  font-size: 16px;
  font-weight: 900;
}

.grid2{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}
@media (max-width: 860px){
  .grid2{ grid-template-columns: 1fr; }
  .header{ align-items:flex-start; flex-direction: column; }
}

.field{ display:grid; gap: 6px; }
.label{ font-size:12px; font-weight:700; color:#374151; }
.input{
  height:42px;
  border-radius:10px;
  border:1px solid rgba(0,0,0,.14);
  padding:0 12px;
  outline:none;
  background:#fff;
}

.value-box{
  min-height:42px;
  border-radius:10px;
  border:1px solid rgba(0,0,0,.14);
  padding:10px 12px;
  background:#f9fafb;
  color:#111827;
  display:flex;
  align-items:center;
}

.hint{
  margin: 12px 0 0;
  color:#6b7280;
  font-size: 12px;
}

.error-text{
  margin: 12px 0 0;
  color: #dc2626;
  font-size: 13px;
}

.success-text{
  margin: 12px 0 0;
  color: #15803d;
  font-size: 13px;
}

.btn{
  height: 40px;
  padding: 0 14px;
  border-radius: 10px;
  border: none;
  cursor:pointer;
  font-weight: 800;
  background:#2563eb;
  color:#fff;
  box-shadow: 0 10px 18px rgba(37,99,235,.18);
}
.btn--ghost{
  background:#f3f4f6;
  color:#111827;
  box-shadow:none;
  border: 1px solid rgba(17,24,39,.10);
}
.btn--danger{
  background:#ef4444;
  box-shadow: 0 10px 18px rgba(239,68,68,.18);
}
</style>


