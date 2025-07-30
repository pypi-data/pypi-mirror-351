<script lang="ts" setup>
const props = defineProps<{
  username: string | null;
}>();
</script>

<template>
  <div>
    <p v-if="props.username">Hello, {{ props.username }}</p>
    <p v-else>You are not logged in. <a href="/admin">Log in!</a></p>
  </div>
</template>

<style scoped>
div {
  text-align: center;
  padding: 2rem 0;
}

p {
  font-size: 2rem;
  font-family: system-ui, Helvetica, Arial, sans-serif;
}
</style>
