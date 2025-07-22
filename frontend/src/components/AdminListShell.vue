<template>
    <div class="man-container">
        <div class="man-header"><h3>{{ title }}</h3></div>

        <div class="man-toolbar">
            <slot name="toolbar"></slot>
        </div>

        <div class="man-list">
            <slot></slot>
        </div>

        <div class="man-pager" v-if="pages > 1">
            <button :disabled="page === 1" @click="$emit('update:page', page - 1)">‹ Prev</button>
            <span>{{ page }}/{{ pages }}</span>
            <button :disabled="page === pages" @click="$emit('update:page', page + 1)">Next ›</button>
        </div>
    </div>
</template>

<script>
export default {
    name: "AdminListShell",
    props: {
        title: { type: String, required: true },
        page: { type: Number, default: 1 },
        pages: { type: Number, default: 1 }
    }
};
</script>

<style scoped>
.man-container {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
}
.man-header {
    margin: 20px;
    padding: 5px;
    font-size: 16px;
    font-weight: bold;
    color: #fff;
}
.man-toolbar {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin: 0 20px 10px;
    justify-content: center;
}
.man-list {
    overflow-y: auto;
    max-height: 50vh;
    width: 100%;
    background: #002f61;
    margin: 0 auto;
    padding: 10px;
    border-radius: 5px;
    color: #fff;
    box-sizing: border-box;
    font-family: sans-serif;
}

.man-list :deep(.user-entry) {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    font-size: 13px;
    padding: 4px 0;
    border-bottom: 1px solid #444;
    flex-wrap: wrap;
}
.man-list :deep(.user-line) {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 80%;
    white-space: nowrap;
}
.man-list :deep(.user-line small) {
    display: block;
    margin: 4px 0 0 0;
    text-align: left;
}
.man-list :deep(.actions) {
    flex: 0 0 auto;
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}
.man-pager {
    margin: 10px auto;
    display: flex;
    gap: 12px;
    align-items: center;
    color: #fff;
}

.man-list :deep(.courses) {
    flex: 0 0 100%;
    margin-top: 4px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    white-space: normal;
}
.man-list :deep(.courses-inline) {
    display: inline-flex;
    gap: 4px;
    align-items: center;
    margin-left: 4px;
}
.man-list :deep(.course-chip) {
    display: inline-block;
    background: rgba(255,255,255,0.1);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
}
.man-list :deep(.link-btn) {
    background: none;
    border: none;
    color: #7ec8ff;
    cursor: pointer;
    padding: 0 2px;
    font-size: 12px;
}
</style>