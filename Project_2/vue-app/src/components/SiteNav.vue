<template>
  <header>
    <section>
      <div class="col1">
        <ul class="inline">
          <li>
            <router-link to="/groups">Groups</router-link>
          </li>
          <li>
            <router-link to="/files">Files</router-link>
          </li>
          <li><a @click="logout()">logout</a></li>
        </ul>
      </div>
    </section>
  </header>
</template>

<script>
export default {
  methods: {
    logout() {
      this.$store.dispatch('logout')
    }
  }
}
</script>
