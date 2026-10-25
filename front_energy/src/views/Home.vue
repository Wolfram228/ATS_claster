<template>
  <div class="home">
    <!-- Блок 1. О проекте -->
    <section class="hero">
      <img :src="img2" alt="Ветроэнергетические установки" class="hero__img" />
      <div class="hero__shade"></div>
      <div class="hero__inner">
        <p class="hero__kicker">О проекте</p>
        <h1 class="hero__title">ТокАналитика</h1>
        <div class="hero__bottom">
          <div class="hero__lead">
            <h2 class="hero__headline">
              ТокАналитика — интеллектуальный анализ рынка электроэнергии.
            </h2>
            <p class="hero__sub">
              Мы объединили разрозненные данные в единую платформу для мониторинга,
              аналитики и прогнозирования. Исследуйте потребление, отслеживайте цены,
              работайте с детализированными таблицами и стройте математические модели (OLS)
              в удобном интерфейсе.
            </p>
          </div>
          <router-link to="/information" class="pill pill--light">
            Начать работу
            <span class="pill__dot">→</span>
          </router-link>
        </div>
      </div>
    </section>

    <!-- Блоки модулей -->
    <section
      v-for="(m, i) in modules"
      :key="m.to"
      class="module"
      :class="{ 'module--reverse': i % 2 === 1 }"
    >
      <div class="module__text">
        <p class="kicker"><span class="kicker__num">0{{ i + 1 }}</span>{{ m.kicker }}</p>
        <h2 class="module__title">{{ m.title }}</h2>
        <p class="module__desc">{{ m.text }}</p>
        <router-link :to="m.to" class="pill">
          {{ m.cta }}
          <span class="pill__dot">→</span>
        </router-link>
      </div>
      <div class="module__media">
        <img :src="m.img" :alt="m.alt" />
      </div>
    </section>
  </div>
</template>

<script>
import img1 from '../assets/1.webp'
import img2 from '../assets/2.webp'
import img3 from '../assets/3.webp'
import img4 from '../assets/4.webp'
import img5 from '../assets/5.webp'

export default {
  name: 'Home',
  data() {
    return {
      img2,
      modules: [
        {
          kicker: 'Информация',
          title: 'Баланс энергосистемы за сутки',
          text: 'Сводные показатели генерации и потребления по ГЭС, АЭС, ТЭС и ВИЭ. Быстрый обзор состояния системы до погружения в детали.',
          to: '/information',
          cta: 'Открыть информацию',
          img: img1,
          alt: 'Гидроэлектростанция'
        },
        {
          kicker: 'Таблица',
          title: 'Почасовые данные в одном срезе',
          text: 'Фильтры по датам, регионам и типам генерации превращают массив наблюдений в рабочую таблицу для сверки и дальнейшего анализа.',
          to: '/table',
          cta: 'Открыть таблицу',
          img: img5,
          alt: 'Электрическая подстанция'
        },
        {
          kicker: 'Карта',
          title: 'География энергосистемы',
          text: 'Интерактивная карта регионов показывает распределение нагрузки и мощностей: сразу видно, где потребление концентрируется.',
          to: '/interactiveMap',
          cta: 'Открыть карту',
          img: img4,
          alt: 'Энергообъект в ландшафте'
        },
        {
          kicker: 'Аналитика цен',
          title: 'Цена электроэнергии во времени',
          text: 'Пики, провалы и сезонные сдвиги оптового рынка. Сопоставляйте цену с нагрузкой и отделяйте шум от устойчивых трендов.',
          to: '/price-analytics',
          cta: 'Смотреть аналитику',
          img: img3,
          alt: 'Солнечная электростанция'
        },
        {
          kicker: 'Моделирование цен',
          title: 'OLS-модель с прозрачными коэффициентами',
          text: 'Выбирайте факторы, оценивайте линейную модель и оценивайте вклад каждой переменной в прогноз цены.',
          to: '/price-modeling',
          cta: 'Перейти к модели',
          img: img2,
          alt: 'Ветроустановки в поле'
        }
      ]
    }
  }
}
</script>

<style scoped>
.home {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px 120px;
  box-sizing: border-box;
  text-align: left;
  color: #0e0e0e;
  background: #fff;
}

/* ---------- Hero ---------- */
.hero {
  position: relative;
  min-height: 680px;
  border-radius: 40px;
  overflow: hidden;
  color: #fff;
}
.hero__img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.hero__shade {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(8, 12, 18, 0.1) 0%, rgba(8, 12, 18, 0.15) 40%, rgba(8, 12, 18, 0.75) 100%);
}
.hero__inner {
  position: relative;
  z-index: 1;
  min-height: 680px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 40px 48px 48px;
  box-sizing: border-box;
}
.hero__kicker {
  margin: 0;
  font-size: 13px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-weight: 600;
}
.hero__title {
  margin: 0;
  font-size: clamp(48px, 11vw, 150px);
  line-height: 0.9;
  font-weight: 600;
  letter-spacing: -0.045em;
  text-transform: uppercase;
}
.hero__bottom {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 40px;
}
.hero__lead {
  max-width: 680px;
}
.hero__headline {
  margin: 0 0 16px;
  font-size: clamp(24px, 2.8vw, 38px);
  line-height: 1.1;
  font-weight: 500;
  letter-spacing: -0.02em;
}
.hero__sub {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.85);
}

/* ---------- Pill button ---------- */
.pill {
  display: inline-flex;
  align-items: center;
  gap: 14px;
  padding: 8px 8px 8px 24px;
  border-radius: 999px;
  background: #0e0e0e;
  color: #fff !important;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  white-space: nowrap;
  transition: transform 0.2s ease;
}
.pill:hover { transform: translateY(-2px); }
.pill__dot {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #fff;
  color: #0e0e0e;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
}
.pill--light { background: #fff; color: #0e0e0e !important; }
.pill--light .pill__dot { background: #0e0e0e; color: #fff; }

/* ---------- Modules ---------- */
.module {
  display: grid;
  grid-template-columns: 1fr 1.1fr;
  gap: 72px;
  align-items: center;
  margin-top: 160px;
}
.module--reverse { grid-template-columns: 1.1fr 1fr; }
.module--reverse .module__text { order: 2; }
.module--reverse .module__media { order: 1; }

.kicker {
  margin: 0 0 28px;
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}
.kicker__num {
  padding: 4px 12px;
  border-radius: 999px;
  background: #f2f2f2;
  letter-spacing: 0.06em;
}
.module__title {
  margin: 0 0 24px;
  font-size: clamp(34px, 4.2vw, 60px);
  line-height: 1.04;
  font-weight: 500;
  letter-spacing: -0.035em;
}
.module__desc {
  margin: 0 0 40px;
  max-width: 46ch;
  font-size: 16px;
  line-height: 1.65;
  color: #6b6b6b;
}
.module__media {
  border-radius: 32px;
  overflow: hidden;
  background: #f4f4f4;
}
.module__media img {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

@media (max-width: 1024px) {
  .module,
  .module--reverse { grid-template-columns: 1fr; gap: 40px; margin-top: 112px; }
  .module--reverse .module__text,
  .module--reverse .module__media { order: initial; }
  .hero__bottom { flex-direction: column; align-items: flex-start; }
}
@media (max-width: 700px) {
  .home { padding: 16px 12px 80px; }
  .hero, .hero__inner { min-height: 560px; border-radius: 28px; }
  .hero__inner { padding: 24px 22px 28px; }
  .module__media { border-radius: 24px; }
}
</style>
